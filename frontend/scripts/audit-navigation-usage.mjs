#!/usr/bin/env node
/*
 * Audits Expo Router layouts, tab/dashboard components, context hook usage,
 * API route usage, JSX props, likely-unused props, and likely-unused imports.
 *
 * Usage:
 *   cd frontend && npm run audit:navigation
 *   node scripts/audit-navigation-usage.mjs --print
 *   node scripts/audit-navigation-usage.mjs ../frontend
 */

import fs from 'node:fs/promises';
import fsSync from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const SOURCE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx']);
const ROUTE_LAYOUT_NAMES = new Set(['_layout.tsx', '_layout.ts', '_layout.jsx', '_layout.js']);
const DEFAULT_SCAN_DIRS = [
  'app',
  'components',
  'contexts',
  'hooks',
  'services',
  'core',
  'types',
  'navigation',
  'screens',
  'constants',
  'utils',
  'theme',
  'lib',
];

const SKIP_DIRS = new Set([
  '.git',
  '.expo',
  '.next',
  'node_modules',
  'coverage',
  'dist',
  'build',
  'ios',
  'android',
]);

const NOISE_FILE_PATTERNS = [
  /(^|\/)frontend_consolidated_export\.txt$/,
  /(^|\/)app_export\.txt$/,
  /(^|\/)app_\(auth\)_export\.txt$/,
  /(^|\/)navigation_export\.txt$/,
  /(^|\/)screens_export\.txt$/,
  /(^|\/)schema_dump/i,
  /(^|\/)db_dump/i,
  /(^|\/)database_dump/i,
  /(^|\/).+_export\.txt$/,
];

function normalizePath(filePath) {
  return filePath.split(path.sep).join('/');
}

function resolveFrontendRoot() {
  const positional = process.argv.find(arg => !arg.startsWith('--') && arg !== process.argv[0] && arg !== process.argv[1]);
  if (positional) return path.resolve(positional);

  const cwd = process.cwd();
  if (fsSync.existsSync(path.join(cwd, 'app')) && fsSync.existsSync(path.join(cwd, 'package.json'))) return cwd;

  const nestedFrontend = path.join(cwd, 'frontend');
  if (fsSync.existsSync(path.join(nestedFrontend, 'app')) && fsSync.existsSync(path.join(nestedFrontend, 'package.json'))) return nestedFrontend;

  return cwd;
}

async function pathExists(candidate) {
  try {
    await fs.access(candidate);
    return true;
  } catch {
    return false;
  }
}

async function walkFiles(rootDir, relativeDir = '') {
  const absoluteDir = path.join(rootDir, relativeDir);
  if (!await pathExists(absoluteDir)) return [];

  const entries = await fs.readdir(absoluteDir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    if (entry.name.startsWith('.') && entry.name !== '.expo') continue;
    const nextRelative = path.join(relativeDir, entry.name);

    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      files.push(...await walkFiles(rootDir, nextRelative));
    } else {
      files.push(normalizePath(nextRelative));
    }
  }

  return files;
}

async function collectFiles(frontendRoot) {
  const fileSet = new Set();
  for (const dir of DEFAULT_SCAN_DIRS) {
    for (const file of await walkFiles(frontendRoot, dir)) fileSet.add(file);
  }
  return [...fileSet].sort();
}

function stripImportBlocks(source) {
  return source
    .replace(/import\s+type\s+[\s\S]*?from\s+['"][^'"]+['"];?/g, '')
    .replace(/import\s+[\s\S]*?from\s+['"][^'"]+['"];?/g, '')
    .replace(/import\s+['"][^'"]+['"];?/g, '');
}

function countIdentifierUsages(source, identifier) {
  if (!identifier) return 0;
  const escaped = identifier.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const matches = source.match(new RegExp(`\\b${escaped}\\b`, 'g'));
  return matches?.length ?? 0;
}

function lineNumberForIndex(source, index) {
  return source.slice(0, index).split('\n').length;
}

function parseImportLocals(clause) {
  if (!clause) return [];

  const cleaned = clause.replace(/^type\s+/, '').replace(/\n/g, ' ').trim();
  const locals = [];

  const namespaceMatch = cleaned.match(/\*\s+as\s+([A-Za-z_$][\w$]*)/);
  if (namespaceMatch) locals.push(namespaceMatch[1]);

  const namedMatch = cleaned.match(/\{([^}]*)\}/);
  if (namedMatch) {
    locals.push(...namedMatch[1]
      .split(',')
      .map(part => part.trim())
      .filter(Boolean)
      .map(part => {
        const alias = part.match(/\bas\s+([A-Za-z_$][\w$]*)$/);
        if (alias) return alias[1];
        return part.replace(/^type\s+/, '').split(/\s+/)[0];
      })
      .filter(Boolean));
  }

  const withoutNamed = cleaned.replace(/\{[^}]*\}/g, '').replace(/\*\s+as\s+[A-Za-z_$][\w$]*/g, '');
  const defaultCandidate = withoutNamed.split(',')[0]?.trim();
  if (defaultCandidate && /^[A-Za-z_$][\w$]*$/.test(defaultCandidate)) locals.push(defaultCandidate);

  return [...new Set(locals)];
}

function parseImports(file, source) {
  const imports = [];
  const importRegex = /import\s+(type\s+)?(?:(?<clause>[\s\S]*?)\s+from\s+)?['"](?<specifier>[^'"]+)['"];?/g;
  let match;

  while ((match = importRegex.exec(source)) !== null) {
    imports.push({
      file,
      specifier: match.groups?.specifier ?? '',
      typeOnly: Boolean(match[1]),
      locals: parseImportLocals(match.groups?.clause ?? ''),
      line: lineNumberForIndex(source, match.index),
    });
  }

  return imports;
}

function parseApiCalls(file, source) {
  const calls = [];
  const apiRegex = /\b(?<client>api|axios)\s*(?:\.\s*(?<method>get|post|put|patch|delete|request))?\s*(?:<[^>]+>)?\s*\(\s*(?<quote>['"`])(?<route>[\s\S]*?)(?<quoteClose>['"`])/g;
  const fetchRegex = /\bfetch\s*\(\s*(?<quote>['"`])(?<route>[\s\S]*?)(?<quoteClose>['"`])/g;

  let match;
  while ((match = apiRegex.exec(source)) !== null) {
    calls.push({ file, client: match.groups.client, method: match.groups.method ?? 'call', route: match.groups.route, line: lineNumberForIndex(source, match.index) });
  }

  while ((match = fetchRegex.exec(source)) !== null) {
    calls.push({ file, client: 'fetch', method: 'call', route: match.groups.route, line: lineNumberForIndex(source, match.index) });
  }

  return calls;
}

function parseContextHooks(file, source) {
  const hooks = [];
  const coreHooks = new Set(['useState', 'useEffect', 'useCallback', 'useMemo', 'useRef', 'useReducer', 'useContext', 'useImperativeHandle', 'useLayoutEffect']);
  const hookRegex = /\b(?<hook>use[A-Z][A-Za-z0-9_]*)\s*\(/g;
  let match;

  while ((match = hookRegex.exec(source)) !== null) {
    const hook = match.groups.hook;
    if (!coreHooks.has(hook)) hooks.push({ file, hook, line: lineNumberForIndex(source, match.index) });
  }

  return hooks;
}

function routeCandidatesForScreen(layoutFile, screenName) {
  const baseDir = path.posix.dirname(layoutFile);
  const normalizedName = screenName.replace(/^\.\//, '').replace(/\/index$/, '/index');
  const base = normalizedName === 'index' ? path.posix.join(baseDir, 'index') : path.posix.join(baseDir, normalizedName);

  const candidates = [];
  for (const ext of SOURCE_EXTENSIONS) candidates.push(`${base}${ext}`);
  for (const ext of SOURCE_EXTENSIONS) candidates.push(`${base}/index${ext}`);
  for (const ext of SOURCE_EXTENSIONS) candidates.push(`${base}/_layout${ext}`);
  return candidates;
}

function parseExpoRouterScreens(file, source, allSourceFiles) {
  if (!ROUTE_LAYOUT_NAMES.has(path.posix.basename(file))) return [];

  const screens = [];
  const screenRegex = /<(?<navigator>Stack|Tabs|Drawer)\.Screen\b[\s\S]*?\bname=(?<quote>['"`])(?<name>[^'"`]+)(?<quoteClose>['"`])[\s\S]*?>/g;
  let match;

  while ((match = screenRegex.exec(source)) !== null) {
    const name = match.groups.name;
    const candidates = routeCandidatesForScreen(file, name);
    const resolved = candidates.find(candidate => allSourceFiles.has(candidate));
    screens.push({ file, navigator: match.groups.navigator, name, line: lineNumberForIndex(source, match.index), resolved: resolved ?? null, candidates });
  }

  return screens;
}

function parseInnerTabs(file, source) {
  const tabs = [];
  const tabItemRegex = /<Tab\.Item\b[\s\S]*?\btitle=(?<quote>['"`])(?<title>[^'"`]+)(?<quoteClose>['"`])[\s\S]*?>/g;
  const tabViewRegex = /<TabView\.Item\b/g;
  let match;

  while ((match = tabItemRegex.exec(source)) !== null) {
    tabs.push({ file, kind: 'Tab.Item', title: match.groups.title, line: lineNumberForIndex(source, match.index) });
  }

  while ((match = tabViewRegex.exec(source)) !== null) {
    tabs.push({ file, kind: 'TabView.Item', title: null, line: lineNumberForIndex(source, match.index) });
  }

  return tabs;
}

function parseNavigationCalls(file, source) {
  const calls = [];
  const routerRegex = /\brouter\.(?<method>push|replace|back|navigate)\s*\(\s*(?<arg>[^)\n]+)/g;
  const linkRegex = /<Link\b[\s\S]*?\bhref=(?<quote>['"`])(?<href>[^'"`]+)(?<quoteClose>['"`])/g;
  let match;

  while ((match = routerRegex.exec(source)) !== null) {
    calls.push({ file, type: 'router', method: match.groups.method, target: match.groups.arg.trim(), line: lineNumberForIndex(source, match.index) });
  }

  while ((match = linkRegex.exec(source)) !== null) {
    calls.push({ file, type: 'Link', method: 'href', target: match.groups.href, line: lineNumberForIndex(source, match.index) });
  }

  return calls;
}

function parsePropsDeclarations(file, source) {
  const declarations = [];
  const interfaceRegex = /interface\s+(?<name>[A-Za-z_$][\w$]*Props)\s*(?:extends\s+[^{]+)?\{(?<body>[\s\S]*?)\n\}/g;
  const typeRegex = /type\s+(?<name>[A-Za-z_$][\w$]*Props)\s*=\s*\{(?<body>[\s\S]*?)\n\}/g;

  for (const regex of [interfaceRegex, typeRegex]) {
    let match;
    while ((match = regex.exec(source)) !== null) {
      const fields = match.groups.body
        .split('\n')
        .map(line => line.trim())
        .map(line => line.match(/^([A-Za-z_$][\w$]*)\??\s*:/)?.[1])
        .filter(Boolean);
      declarations.push({ file, name: match.groups.name, component: match.groups.name.replace(/Props$/, ''), fields: [...new Set(fields)], line: lineNumberForIndex(source, match.index), start: match.index, end: regex.lastIndex });
    }
  }

  return declarations;
}

function buildPropUsageAudit(file, source, declarations) {
  const audits = [];

  for (const declaration of declarations) {
    const sourceWithoutDeclaration = `${source.slice(0, declaration.start)}${source.slice(declaration.end)}`;
    const fields = declaration.fields.map(field => {
      const references = countIdentifierUsages(sourceWithoutDeclaration, field);
      return { name: field, references, status: references > 0 ? 'used' : 'likely-unused' };
    });
    audits.push({ file, name: declaration.name, component: declaration.component, line: declaration.line, fields });
  }

  return audits;
}

function parseJsxProps(file, source) {
  const usages = [];
  const jsxRegex = /<(?<component>[A-Z][A-Za-z0-9_.]*)\b(?<attrs>[^<>]*?)(?:\/?>)/g;
  let match;

  while ((match = jsxRegex.exec(source)) !== null) {
    const attrs = match.groups.attrs ?? '';
    const props = [];
    const propRegex = /(?:^|\s)(?<name>[A-Za-z_$][\w$-]*)(?:\s*=|\s|$)/g;
    let propMatch;
    while ((propMatch = propRegex.exec(attrs)) !== null) {
      const propName = propMatch.groups.name;
      if (!['key', 'style', 'children'].includes(propName)) props.push(propName);
    }

    if (props.length > 0) {
      usages.push({ file, component: match.groups.component, props: [...new Set(props)].sort(), line: lineNumberForIndex(source, match.index) });
    }
  }

  return usages;
}

function likelyUnusedImports(file, source, imports) {
  const withoutImports = stripImportBlocks(source);
  const unused = [];

  for (const importEntry of imports) {
    for (const local of importEntry.locals) {
      if (countIdentifierUsages(withoutImports, local) === 0) {
        unused.push({ file, local, specifier: importEntry.specifier, line: importEntry.line, confidence: importEntry.typeOnly ? 'medium' : 'high' });
      }
    }
  }

  return unused;
}

function groupBy(items, keyFn) {
  const grouped = new Map();
  for (const item of items) {
    const key = keyFn(item);
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(item);
  }
  return Object.fromEntries(grouped.entries());
}

function summarizeImports(imports) {
  return Object.entries(groupBy(imports, item => item.specifier))
    .map(([specifier, entries]) => ({ specifier, count: entries.length, files: [...new Set(entries.map(entry => entry.file))].sort() }))
    .sort((a, b) => b.count - a.count || a.specifier.localeCompare(b.specifier));
}

function summarizeApiCalls(apiCalls) {
  return Object.entries(groupBy(apiCalls, item => `${item.client}.${item.method} ${item.route}`))
    .map(([signature, entries]) => ({ signature, count: entries.length, files: entries.map(entry => `${entry.file}:${entry.line}`).sort() }))
    .sort((a, b) => b.count - a.count || a.signature.localeCompare(b.signature));
}

function summarizeContextHooks(hooks) {
  return Object.entries(groupBy(hooks, item => item.hook))
    .map(([hook, entries]) => ({ hook, count: entries.length, files: entries.map(entry => `${entry.file}:${entry.line}`).sort() }))
    .sort((a, b) => b.count - a.count || a.hook.localeCompare(b.hook));
}

function flattenLikelyUnusedProps(propUsageAudit) {
  return propUsageAudit.flatMap(entry => entry.fields
    .filter(field => field.status === 'likely-unused')
    .map(field => ({ file: entry.file, component: entry.component, propsType: entry.name, prop: field.name, line: entry.line })));
}

function noiseFiles(allFiles) {
  return allFiles.filter(file => NOISE_FILE_PATTERNS.some(pattern => pattern.test(file))).sort();
}

function makeMarkdownReport(report) {
  const missingScreens = report.routeScreens.filter(screen => !screen.resolved);
  const lines = [];

  lines.push('# Navigation Usage Audit');
  lines.push('');
  lines.push(`Generated at: ${new Date(report.generatedAt).toISOString()}`);
  lines.push(`Frontend root: \`${report.frontendRoot}\``);
  lines.push('');
  lines.push('## Summary');
  lines.push('');
  lines.push(`- Source files scanned: ${report.summary.sourceFiles}`);
  lines.push(`- Imports found: ${report.summary.imports}`);
  lines.push(`- Expo Router screen declarations: ${report.summary.routeScreens}`);
  lines.push(`- Missing/unresolved route screen targets: ${missingScreens.length}`);
  lines.push(`- Inner dashboard tab declarations: ${report.summary.innerTabs}`);
  lines.push(`- Navigation calls: ${report.summary.navigationCalls}`);
  lines.push(`- Context hook usages: ${report.summary.contextHooks}`);
  lines.push(`- API calls: ${report.summary.apiCalls}`);
  lines.push(`- Props declarations: ${report.summary.propDeclarations}`);
  lines.push(`- JSX prop usage sites: ${report.summary.jsxPropUsages}`);
  lines.push(`- Likely-unused props: ${report.summary.likelyUnusedProps}`);
  lines.push(`- Likely-unused imports: ${report.summary.likelyUnusedImports}`);
  lines.push(`- Generated/export/db/schema noise candidates: ${report.summary.noiseCandidates}`);
  lines.push('');

  lines.push('## Expo Router Screens');
  lines.push('');
  for (const screen of report.routeScreens) lines.push(`- \`${screen.file}:${screen.line}\` ${screen.navigator}.Screen \`${screen.name}\` -> ${screen.resolved ? `\`${screen.resolved}\`` : '**missing target**'}`);
  if (report.routeScreens.length === 0) lines.push('- No Expo Router screen declarations found.');
  lines.push('');

  if (missingScreens.length > 0) {
    lines.push('## Missing Route Targets');
    lines.push('');
    for (const screen of missingScreens) lines.push(`- \`${screen.file}:${screen.line}\` declares \`${screen.name}\`; checked: ${screen.candidates.map(candidate => `\`${candidate}\``).join(', ')}`);
    lines.push('');
  }

  lines.push('## Inner Tabs / TabView');
  lines.push('');
  for (const tab of report.innerTabs) lines.push(`- \`${tab.file}:${tab.line}\` ${tab.kind}${tab.title ? ` \`${tab.title}\`` : ''}`);
  if (report.innerTabs.length === 0) lines.push('- No RNEUI Tab or TabView items found.');
  lines.push('');

  lines.push('## Navigation Calls');
  lines.push('');
  for (const call of report.navigationCalls) lines.push(`- \`${call.file}:${call.line}\` ${call.type}.${call.method} -> \`${call.target}\``);
  if (report.navigationCalls.length === 0) lines.push('- No router/Link navigation calls found.');
  lines.push('');

  lines.push('## Context Hook Usage');
  lines.push('');
  for (const hook of report.contextHookSummary) lines.push(`- \`${hook.hook}\` (${hook.count}): ${hook.files.map(file => `\`${file}\``).join(', ')}`);
  if (report.contextHookSummary.length === 0) lines.push('- No non-core hooks found.');
  lines.push('');

  lines.push('## API Calls');
  lines.push('');
  for (const api of report.apiSummary) lines.push(`- \`${api.signature}\` (${api.count}): ${api.files.map(file => `\`${file}\``).join(', ')}`);
  if (report.apiSummary.length === 0) lines.push('- No direct API calls found.');
  lines.push('');

  lines.push('## Props Declared + Usage Heuristic');
  lines.push('');
  lines.push('The prop usage check removes the Props declaration from the file, then counts references to each field in the rest of that file. Confirm with TypeScript before deleting.');
  lines.push('');
  for (const declaration of report.propUsageAudit) {
    lines.push(`- \`${declaration.file}:${declaration.line}\` ${declaration.name}: ${declaration.fields.map(field => `\`${field.name}\`=${field.status}(${field.references})`).join(', ') || '_no fields parsed_'}`);
  }
  if (report.propUsageAudit.length === 0) lines.push('- No Props interfaces/types found.');
  lines.push('');

  lines.push('## JSX Prop Usage Sites');
  lines.push('');
  for (const usage of report.jsxPropUsages) lines.push(`- \`${usage.file}:${usage.line}\` <${usage.component}>: ${usage.props.map(prop => `\`${prop}\``).join(', ')}`);
  if (report.jsxPropUsages.length === 0) lines.push('- No JSX prop usage sites found.');
  lines.push('');

  lines.push('## Likely-Unused Imports');
  lines.push('');
  lines.push('This is a regex-based signal. Confirm with TypeScript/ESLint before deleting.');
  lines.push('');
  for (const unused of report.likelyUnusedImports) lines.push(`- \`${unused.file}:${unused.line}\` \`${unused.local}\` from \`${unused.specifier}\` (${unused.confidence})`);
  if (report.likelyUnusedImports.length === 0) lines.push('- No likely-unused imports found by this heuristic.');
  lines.push('');

  lines.push('## Import Summary');
  lines.push('');
  for (const item of report.importSummary.slice(0, 80)) lines.push(`- \`${item.specifier}\` (${item.count} files)`);
  if (report.importSummary.length > 80) lines.push(`- ...and ${report.importSummary.length - 80} more import specifiers. See JSON for full output.`);
  if (report.importSummary.length === 0) lines.push('- No imports found.');
  lines.push('');

  lines.push('## Noise Candidates');
  lines.push('');
  lines.push('These are generated exports, dumps, or schema/db artifacts that should not drive navigation logic. Review before deletion.');
  lines.push('');
  for (const file of report.noiseCandidates) lines.push(`- \`${file}\``);
  if (report.noiseCandidates.length === 0) lines.push('- No obvious generated export/db/schema noise candidates found.');
  lines.push('');

  return `${lines.join('\n')}\n`;
}

async function main() {
  const frontendRoot = resolveFrontendRoot();
  const sourceFiles = await collectFiles(frontendRoot);
  const allFiles = await walkFiles(frontendRoot);
  const allSourceFileSet = new Set(sourceFiles.filter(file => SOURCE_EXTENSIONS.has(path.extname(file))));

  const imports = [];
  const apiCalls = [];
  const contextHooks = [];
  const routeScreens = [];
  const innerTabs = [];
  const navigationCalls = [];
  const propDeclarations = [];
  const propUsageAudit = [];
  const jsxPropUsages = [];
  const likelyUnused = [];

  for (const file of sourceFiles) {
    if (!SOURCE_EXTENSIONS.has(path.extname(file))) continue;
    const absolute = path.join(frontendRoot, file);
    const source = await fs.readFile(absolute, 'utf8');
    const fileImports = parseImports(file, source);
    const filePropDeclarations = parsePropsDeclarations(file, source);

    imports.push(...fileImports);
    apiCalls.push(...parseApiCalls(file, source));
    contextHooks.push(...parseContextHooks(file, source));
    routeScreens.push(...parseExpoRouterScreens(file, source, allSourceFileSet));
    innerTabs.push(...parseInnerTabs(file, source));
    navigationCalls.push(...parseNavigationCalls(file, source));
    propDeclarations.push(...filePropDeclarations);
    propUsageAudit.push(...buildPropUsageAudit(file, source, filePropDeclarations));
    jsxPropUsages.push(...parseJsxProps(file, source));
    likelyUnused.push(...likelyUnusedImports(file, source, fileImports));
  }

  const likelyUnusedProps = flattenLikelyUnusedProps(propUsageAudit);
  const report = {
    generatedAt: new Date().toISOString(),
    frontendRoot: normalizePath(frontendRoot),
    summary: {
      sourceFiles: allSourceFileSet.size,
      imports: imports.length,
      routeScreens: routeScreens.length,
      innerTabs: innerTabs.length,
      navigationCalls: navigationCalls.length,
      contextHooks: contextHooks.length,
      apiCalls: apiCalls.length,
      propDeclarations: propDeclarations.length,
      jsxPropUsages: jsxPropUsages.length,
      likelyUnusedProps: likelyUnusedProps.length,
      likelyUnusedImports: likelyUnused.length,
      noiseCandidates: noiseFiles(allFiles).length,
    },
    routeScreens,
    innerTabs,
    navigationCalls,
    contextHookSummary: summarizeContextHooks(contextHooks),
    contextHooks,
    apiSummary: summarizeApiCalls(apiCalls),
    apiCalls,
    propDeclarations,
    propUsageAudit,
    likelyUnusedProps,
    jsxPropUsages,
    likelyUnusedImports: likelyUnused.sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line),
    importSummary: summarizeImports(imports),
    imports,
    noiseCandidates: noiseFiles(allFiles),
  };

  const markdown = makeMarkdownReport(report);

  if (process.argv.includes('--print')) {
    process.stdout.write(markdown);
    return;
  }

  const auditsDir = path.join(frontendRoot, 'audits');
  await fs.mkdir(auditsDir, { recursive: true });
  await fs.writeFile(path.join(auditsDir, 'navigation-usage-report.json'), `${JSON.stringify(report, null, 2)}\n`);
  await fs.writeFile(path.join(auditsDir, 'navigation-usage-report.md'), markdown);

  console.log(`Navigation usage audit written to ${normalizePath(path.join(auditsDir, 'navigation-usage-report.md'))}`);
  console.log(`JSON audit written to ${normalizePath(path.join(auditsDir, 'navigation-usage-report.json'))}`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

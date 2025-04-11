# UI Directory

This directory contains user interface components for the ADHD Calendar backend application.

## Overview

The UI directory houses backend components related to user interface rendering, templating, and UI-specific utilities. While the main user interface is implemented in the frontend application, these components support server-side rendering, administrative interfaces, and embedded UI elements.

## Components

- **templates/**: HTML templates for server-rendered pages
- **static/**: Static assets like CSS, JavaScript, and images
- **admin/**: Admin panel UI components
- **email/**: Email template components
- **components/**: Reusable UI components
- **renderers/**: Custom renderers for different output formats

## Templates

The templates directory contains Jinja2 templates for server-rendered pages:

- **base.html**: Base template with common layout elements
- **auth/**: Authentication-related templates
- **admin/**: Administrative interface templates
- **email/**: Email templates
- **error/**: Error page templates

## Static Assets

Static assets are organized by type:

- **css/**: Stylesheets
- **js/**: JavaScript files
- **img/**: Images
- **fonts/**: Font files

## Admin Interface

The admin directory contains components for the administrative interface:

- **views/**: Admin view implementations
- **forms/**: Admin form definitions
- **widgets/**: Custom admin widgets
- **filters/**: Admin list filters

## Email Templates

Email templates for various notifications:

- **welcome.html**: New user welcome email
- **password_reset.html**: Password reset email
- **task_reminder.html**: Task reminder email
- **summary.html**: Daily/weekly summary email

## Usage Example

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="app/ui/templates")
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

@app.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "data": get_dashboard_data()}
    )
```

## Development Guidelines

When working with UI components:

1. Maintain consistent styling and design patterns
2. Keep templates modular and reusable
3. Separate logic from presentation
4. Optimize assets for performance
5. Ensure accessibility compliance
6. Test across different browsers and devices

## Integration with Frontend

The backend UI components integrate with the React Native frontend through:

- API endpoints that deliver UI configuration
- Shared styling constants for consistent appearance
- Email templates that match the application's design
- Administrative interfaces for content management

## Related Documentation

- [Template System](../../docs/template_system.md)
- [Admin Interface Guide](../../docs/admin_interface.md)
- [Email Template Guide](../../docs/email_templates.md)
- [UI/UX Guidelines](../../docs/ui_guidelines.md)

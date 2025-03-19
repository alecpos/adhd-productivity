# Epic 3: Visual Reference Document - Part 1
# Proactive Forgetfulness and Distraction Mitigation

## System Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Applications                         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API Gateway / Load Balancer                    │
└───────────┬──────────────────┬───────────────────┬──────────────────┘
            │                  │                   │
            ▼                  ▼                   ▼
┌────────────────────┐ ┌────────────────┐ ┌────────────────────┐
│Commitment Detection│ │Dialogue System  │ │Smart Reminder      │
│Service             │ │Service          │ │Service             │
└─────────┬──────────┘ └────────┬───────┘ └──────────┬─────────┘
          │                     │                    │
          │                     ▼                    │
          │         ┌────────────────────────┐      │
          └────────►│  Commitment and        │◄─────┘
                    │  Context Database      │
                    └────────────┬───────────┘
                                 │
                                 ▼
                   ┌─────────────────────────────┐
                   │Notification Service         │
                   │                             │
                   └─────────────────────────────┘
```

### Service Communication Patterns

```
┌───────────────────┐      HTTP/REST       ┌───────────────────┐
│                   │◄────────────────────►│                   │
│   API Gateway     │                      │  Mobile App       │
│                   │                      │                   │
└────────┬──────────┘                      └───────────────────┘
         │
         │ gRPC
         │
┌────────▼──────────┐                     ┌───────────────────┐
│                   │    Message Queue    │                   │
│  Service Registry │◄────────────────────►│  Event Bus        │
│                   │                     │                   │
└────────┬──────────┘                     └───────────────────┘
         │
         │ gRPC
         ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    Microservice Mesh                        │
│                                                             │
└──┬─────────────┬───────────────┬────────────────┬───────────┘
   │             │               │                │
   │ gRPC        │ gRPC          │ gRPC           │ WebSocket
   ▼             ▼               ▼                ▼
┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌───────────────┐
│         │  │         │  │             │  │               │
│Detection│  │Dialogue │  │Reminder     │  │Notification   │
│Service  │  │Service  │  │Service      │  │Service        │
│         │  │         │  │             │  │               │
└─────────┘  └─────────┘  └─────────────┘  └───────────────┘
```

### Database Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Database Cluster                      │
│                                                         │
│  ┌─────────────┐     ┌─────────────┐    ┌─────────────┐ │
│  │             │     │             │    │             │ │
│  │   Primary   │────►│  Read       │    │  Read       │ │
│  │   Node      │     │  Replica    │    │  Replica    │ │
│  │             │     │             │    │             │ │
│  └─────────────┘     └─────────────┘    └─────────────┘ │
│         ▲                                               │
└─────────┼───────────────────────────────────────────────┘
          │
          │ Write Operations
          │
┌─────────▼───────────────────────────────────────────────┐
│                                                         │
│                 Application Services                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
          │
          │ Read Operations
          ▼
┌─────────────────────────────────────────────────────────┐
│                    Cache Layer                          │
│                                                         │
│  ┌─────────────┐     ┌─────────────┐    ┌─────────────┐ │
│  │             │     │             │    │             │ │
│  │  Redis      │     │  In-Memory  │    │  CDN        │ │
│  │  Cache      │     │  Cache      │    │  Cache      │ │
│  │             │     │             │    │             │ │
│  └─────────────┘     └─────────────┘    └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### MongoDB Collection Relationships

```
┌───────────────────────────────┐
│      CommitmentModel          │
├───────────────────────────────┤
│ _id: ObjectId                 │
│ user_id: UUID                 │──────┐
│ text: String                  │      │
│ source: String                │      │
│ confidence: Float             │      │
│ due_date: DateTime            │      │
│ priority: String              │      │
│ status: String                │      │
│ created_at: DateTime          │      │
└───────────────────────────────┘      │
                                       │
┌───────────────────────────────┐      │
│   DialogueSessionModel        │      │
├───────────────────────────────┤      │
│ _id: ObjectId                 │      │
│ user_id: UUID                 │──────┘
│ context: JSON                 │      
│ message_history: Array        │      
│ created_at: DateTime          │      
│ last_active: DateTime         │      
└───────────────────────────────┘      
                                       
┌───────────────────────────────┐      
│   ReminderModel               │      
├───────────────────────────────┤      
│ _id: ObjectId                 │      
│ commitment_id: ObjectId ──────┼──────┐
│ user_id: UUID                 │      │
│ scheduled_time: DateTime      │      │
│ context: JSON                 │      │
│ priority: String              │      │
│ status: String                │      │
│ created_at: DateTime          │      │
└───────────────────────────────┘      │
                                       │
┌───────────────────────────────┐      │
│   UserContextModel            │      │
├───────────────────────────────┤      │
│ _id: ObjectId                 │      │
│ user_id: UUID                 │      │
│ location: String              │      │
│ device: String                │      │
│ activity: String              │      │
│ focus_level: Integer          │      │
│ commitments: [ObjectId] ──────┼──────┘
│ updated_at: DateTime          │
└───────────────────────────────┘
``` 

# Epic 3: Visual Reference Document - Part 2
# Data Flow and Component Interaction

## Data Flow Diagrams

### Commitment Detection Flow

```
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│               │    │                 │    │                 │
│ User Text     │───►│ Text Processing │───►│ Pattern         │
│ Input         │    │ Pipeline        │    │ Recognition     │
│               │    │                 │    │                 │
└───────────────┘    └─────────────────┘    └────────┬────────┘
                                                     │
┌───────────────┐    ┌─────────────────┐    ┌────────▼────────┐
│               │    │                 │    │                 │
│ Commitment    │◄───│ Confidence      │◄───│ LLM-Based       │
│ Storage       │    │ Evaluation      │    │ Analysis        │
│               │    │                 │    │                 │
└───────────────┘    └─────────────────┘    └─────────────────┘
                            ▲
                            │
                     ┌──────┴──────┐
                     │             │
                     │ Temporal    │
                     │ Extraction  │
                     │             │
                     └─────────────┘
```

### Dialogue System Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│ User         │─────►│ Natural      │─────►│ Context      │
│ Message      │      │ Language     │      │ Management   │
│              │      │ Understanding│      │              │
└──────────────┘      └──────────────┘      └──────┬───────┘
                                                   │
┌──────────────┐      ┌──────────────┐      ┌──────▼───────┐
│              │      │              │      │              │
│ Dialogue     │◄─────│ Response     │◄─────│ Commitment   │
│ Interface    │      │ Generation   │      │ Retrieval    │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
```

### Smart Reminder Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│ Commitment    │────►│ Priority      │────►│ Context       │
│ Database      │     │ Assessment    │     │ Awareness     │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│ User          │◄────│ Notification  │◄────│ Timing        │
│ Device        │     │ Delivery      │     │ Optimization  │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### User Feedback and Learning Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│ User          │────►│ Reminder      │────►│ Effectiveness │
│ Interaction   │     │ Response      │     │ Analysis      │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│ Improved      │◄────│ Model         │◄────│ Pattern       │
│ Reminders     │     │ Updates       │     │ Recognition   │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

## Component Interaction Diagrams

### CommitmentDetectionService Components

```
┌─────────────────────────────────────────────────────────────┐
│                 CommitmentDetectionService                  │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Text Source   │──►│ NLP           │──►│ Regex         │  │
│  │ Connectors    │   │ Preprocessor  │   │ Patterns      │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Confidence    │◄──┤ Pattern       │◄──┤ LLM           │  │
│  │ Scoring       │   │ Merger        │   │ Detector      │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Temporal      │──►│ Priority      │──►│ Commitment    │  │
│  │ Extraction    │   │ Assignment    │   │ Repository    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### DialogueSystemService Components

```
┌─────────────────────────────────────────────────────────────┐
│                     DialogueSystemService                   │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Message       │──►│ Intent        │──►│ Entity        │  │
│  │ Receiver      │   │ Recognition   │   │ Extraction    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Response      │◄──┤ Context       │◄──┤ Commitment    │  │
│  │ Generator     │   │ Manager       │   │ Lookup        │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Natural       │──►│ Session       │──►│ Commitment    │  │
│  │ Language      │   │ Management    │   │ Extractor     │  │
│  │ Generator     │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### SmartReminderService Components

```
┌─────────────────────────────────────────────────────────────┐
│                   SmartReminderService                      │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Commitment    │──►│ Priority      │──►│ Context       │  │
│  │ Monitor       │   │ Calculator    │   │ Analyzer      │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Notification  │◄──┤ Timing        │◄──┤ User State    │  │
│  │ Composer      │   │ Optimizer     │   │ Detector      │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Delivery      │──►│ Feedback      │──►│ Learning      │  │
│  │ Manager       │   │ Collector     │   │ Engine        │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ContextManagementService Components

```
┌─────────────────────────────────────────────────────────────┐
│                   ContextManagementService                  │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Sensor        │──►│ Location      │──►│ Activity      │  │
│  │ Integration   │   │ Tracking      │   │ Recognition   │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Context       │◄──┤ Pattern       │◄──┤ Device        │  │
│  │ Repository    │   │ Recognition   │   │ Monitoring    │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ User State    │──►│ Privacy       │──►│ Context       │  │
│  │ Analyzer      │   │ Filter        │   │ API           │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling Patterns

### Graceful Degradation for Commitment Detection

```typescript
/**
 * A robust commitment detector that gracefully degrades when services are unavailable
 * This pattern allows the app to continue functioning with reduced capabilities
 */
class RobustCommitmentDetector {
  private readonly fallbackPatterns = [
    /(?:need to|must|should|have to|going to)\s+(\w+\s+(?:by|before|on|next|tomorrow|tonight|today))/i,
    /(?:don't forget to|remember to)\s+(.+?)(?:\s+by|\s+on|\s+before|$)/i
  ];
  
  /**
   * Multi-level detection with fallbacks
   */
  async detectCommitments(text: string): Promise<DetectedCommitment[]> {
    try {
      // Try the advanced AI service first
      return await this.runAIDetection(text);
    } catch (error) {
      console.warn('AI detection failed, falling back to rules engine', error);
      
      try {
        // Local NLP as first fallback
        return await this.runLocalNLP(text);
      } catch (localError) {
        console.warn('Local NLP detection failed, using basic patterns', localError);
        
        // Last resort: simple pattern matching
        return this.runBasicPatternDetection(text);
      }
    }
  }
  
  /**
   * Basic pattern matching as last resort
   */
  private runBasicPatternDetection(text: string): DetectedCommitment[] {
    const commitments: DetectedCommitment[] = [];
    
    for (const pattern of this.fallbackPatterns) {
      const matches = [...text.matchAll(pattern)];
      
      for (const match of matches) {
        commitments.push({
          text: match[0],
          confidence: 0.5, // Lower confidence for fallback detection
          dueDate: null,
          priority: 'medium'
        });
      }
    }
    
    return commitments;
  }
  
  // Other methods omitted for brevity
}
```

### Centralized Error Handling

```typescript
/**
 * A centralized error handler that provides consistent error handling
 * across different components of the commitment detection system
 */
class CommitmentSystemErrorHandler {
  private static instance: CommitmentSystemErrorHandler;
  private telemetryEnabled: boolean = true;
  private errorCallbacks: Map<string, (error: any) => void> = new Map();
  
  private constructor() {
    // Initialize error tracking
    this.setupGlobalErrorListeners();
  }
  
  /**
   * Get singleton instance
   */
  public static getInstance(): CommitmentSystemErrorHandler {
    if (!CommitmentSystemErrorHandler.instance) {
      CommitmentSystemErrorHandler.instance = new CommitmentSystemErrorHandler();
    }
    return CommitmentSystemErrorHandler.instance;
  }
  
  /**
   * Handle errors with appropriate response based on type
   */
  public handleError(error: any, context: string): void {
    // Log all errors
    console.error(`Error in ${context}:`, error);
    
    // Send telemetry if enabled
    if (this.telemetryEnabled) {
      this.sendErrorTelemetry(error, context);
    }
    
    // Categorize and handle based on error type
    if (this.isNetworkError(error)) {
      this.handleNetworkError(error, context);
    } else if (this.isAuthError(error)) {
      this.handleAuthError(error);
    } else if (this.isInputValidationError(error)) {
      this.handleValidationError(error, context);
    } else {
      this.handleUnknownError(error, context);
    }
    
    // Notify any registered callbacks
    if (this.errorCallbacks.has(context)) {
      this.errorCallbacks.get(context)!(error);
    }
  }
  
  /**
   * Register callback for specific context
   */
  public registerErrorCallback(context: string, callback: (error: any) => void): void {
    this.errorCallbacks.set(context, callback);
  }
  
  /**
   * Handle network connectivity issues
   */
  private handleNetworkError(error: any, context: string): void {
    // Update UI state to show offline mode
    this.updateOfflineStatus(true);
    
    // Check if we have cached data that can be used
    const cachedData = this.getCachedData(context);
    if (cachedData) {
      this.useCachedData(context, cachedData);
    }
    
    // Setup a retry mechanism
    this.scheduleRetry(context);
    
    // Show user-friendly message
    this.showUserMessage(
      'You appear to be offline. Some features may be limited until connection is restored.'
    );
  }
  
  /**
   * Handle authentication errors
   */
  private handleAuthError(error: any): void {
    // Clear invalid credentials
    this.clearAuthTokens();
    
    // Redirect to login
    this.redirectToLogin({
      reason: 'session_expired',
      returnUrl: getCurrentRoute()
    });
  }
  
  /**
   * Detect error types
   */
  private isNetworkError(error: any): boolean {
    return (
      error instanceof TypeError && 
      (error.message.includes('Network request failed') || 
       error.message.includes('Failed to fetch')) ||
      error.name === 'NetworkError' ||
      error.code === 'ERR_NETWORK'
    );
  }
  
  private isAuthError(error: any): boolean {
    return (
      (error.status === 401 || error.statusCode === 401) ||
      error.message.includes('unauthorized') ||
      error.message.includes('authentication required')
    );
  }
  
  private isInputValidationError(error: any): boolean {
    return (
      (error.status === 400 || error.statusCode === 400) ||
      error.name === 'ValidationError' ||
      (error.errors && Array.isArray(error.errors))
    );
  }
  
  // Additional helper methods omitted for brevity
}
```

## Knowledge Graph Visualization

### Documentation Knowledge Graph Structure

```
┌─────────────────────────────────────────────────────────────┐
│                   Knowledge Graph System                     │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Model         │───┤ Pattern       │───┤ Dataset       │  │
│  │ Documentation │   │ Connection    │   │ Documentation │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────┬───────┘  │
│          │                                       │          │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Implementation│   │ Dependency    │   │ Schema        │  │
│  │ Details       │───┤ Graph         │───┤ Definition    │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────┬───────┘   └───────┬───────┘  │
│          │                   │                   │          │
│  ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ API           │───┤ Example       │───┤ Validation    │  │
│  │ Documentation │   │ Usage         │   │ Rules         │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Knowledge Graph Implementation

```typescript
/**
 * Knowledge graph implementation for organizing and visualizing documentation relationships
 * within the commitment detection and reminder system
 */
class DocumentationGraph {
  private nodes: Map<string, DocNode> = new Map();
  private edges: Edge[] = [];
  
  /**
   * Add a documentation node to the graph
   */
  public addNode(node: DocNode): string {
    const id = node.id || this.generateNodeId(node.title);
    this.nodes.set(id, { ...node, id });
    return id;
  }
  
  /**
   * Create a relationship between two documentation nodes
   */
  public addEdge(sourceId: string, targetId: string, type: EdgeType, metadata?: Record<string, any>): boolean {
    if (!this.nodes.has(sourceId) || !this.nodes.has(targetId)) {
      console.error(`Cannot create edge: node not found`);
      return false;
    }
    
    this.edges.push({
      source: sourceId,
      target: targetId,
      type,
      metadata: metadata || {}
    });
    
    return true;
  }
  
  /**
   * Traverse the graph from a starting node to find all related documentation
   */
  public traverseRelated(startNodeId: string, maxDepth: number = 2): DocNode[] {
    if (!this.nodes.has(startNodeId)) return [];
    
    const visited = new Set<string>();
    const result: DocNode[] = [];
    
    const traverse = (nodeId: string, depth: number) => {
      if (visited.has(nodeId) || depth > maxDepth) return;
      
      visited.add(nodeId);
      const node = this.nodes.get(nodeId);
      if (node) result.push(node);
      
      // Find all edges connected to this node
      const connectedEdges = this.edges.filter(
        edge => edge.source === nodeId || edge.target === nodeId
      );
      
      // Follow each connection
      for (const edge of connectedEdges) {
        const nextNodeId = edge.source === nodeId ? edge.target : edge.source;
        traverse(nextNodeId, depth + 1);
      }
    };
    
    traverse(startNodeId, 0);
    return result;
  }
  
  /**
   * Export the graph as a visualizable format
   */
  public exportVisualization(): GraphVisualization {
    return {
      nodes: Array.from(this.nodes.values()).map(node => ({
        id: node.id,
        label: node.title,
        type: node.type,
        tags: node.tags || []
      })),
      edges: this.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        type: edge.type,
        label: this.getEdgeLabel(edge.type)
      }))
    };
  }
  
  /**
   * Generate a visualization of documentation connected to a commitment pattern
   */
  public visualizeCommitmentDocumentation(commitmentId: string): string {
    const nodes = this.traverseRelated(commitmentId);
    
    // Generate a DOT format for visualization
    let dot = 'digraph CommitmentDocs {\n';
    dot += '  rankdir=LR;\n';
    dot += '  node [shape=box, style=filled, fillcolor=lightblue];\n';
    
    // Add nodes
    for (const node of nodes) {
      const color = this.getNodeColor(node.type);
      dot += `  "${node.id}" [label="${node.title}", fillcolor="${color}"];\n`;
    }
    
    // Add edges
    for (const edge of this.edges) {
      if (nodes.some(n => n.id === edge.source) && nodes.some(n => n.id === edge.target)) {
        dot += `  "${edge.source}" -> "${edge.target}" [label="${this.getEdgeLabel(edge.type)}"];\n`;
      }
    }
    
    dot += '}';
    return dot;
  }
  
  private getNodeColor(type: NodeType): string {
    const colors: Record<NodeType, string> = {
      'model': '#c5e8f7',
      'dataset': '#f7e8c5',
      'service': '#d5f7c5',
      'api': '#f7c5e8',
      'documentation': '#e8c5f7'
    };
    return colors[type] || 'lightblue';
  }
  
  private getEdgeLabel(type: EdgeType): string {
    const labels: Record<EdgeType, string> = {
      'depends_on': 'depends on',
      'implements': 'implements',
      'documents': 'documents',
      'uses': 'uses',
      'extends': 'extends'
    };
    return labels[type] || type;
  }
  
  private generateNodeId(title: string): string {
    // Generate a simple ID from the title
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/(^_+|_+$)/g, '');
  }
}

/**
 * Usage example:
 * 
 * // Create the documentation graph
 * const docGraph = new DocumentationGraph();
 * 
 * // Add documentation nodes
 * const commitmentModelId = docGraph.addNode({
 *   title: 'Commitment Detection Model',
 *   type: 'model',
 *   path: '/models/commitment_detection.py',
 *   tags: ['nlp', 'core', 'detection']
 * });
 * 
 * const dataSchemaId = docGraph.addNode({
 *   title: 'Commitment Data Schema',
 *   type: 'documentation',
 *   path: '/docs/schemas/commitment.md',
 *   tags: ['schema', 'data']
 * });
 * 
 * // Create relationships
 * docGraph.addEdge(dataSchemaId, commitmentModelId, 'documents');
 * 
 * // Generate visualization for all docs related to the commitment model
 * const visualization = docGraph.visualizeCommitmentDocumentation(commitmentModelId);
 */
```

### Semantic Network for Commitment Contexts

```
┌───────────────────────────────────────────────────────────────────┐
│                     Commitment Context Graph                       │
│                                                                   │
│                ┌───────────┐         ┌───────────┐                │
│                │           │         │           │                │
│                │ Location  ├─────────┤ Activity  │                │
│                │ Context   │         │ Context   │                │
│                │           │         │           │                │
│                └─────┬─────┘         └─────┬─────┘                │
│                      │                     │                      │
│                      │     ┌─────────┐     │                      │
│                      │     │         │     │                      │
│                      └─────┤  User   ├─────┘                      │
│                            │ Context │                            │
│                      ┌─────┤         ├─────┐                      │
│                      │     └─────────┘     │                      │
│                      │                     │                      │
│                ┌─────┴─────┐         ┌─────┴─────┐                │
│                │           │         │           │                │
│                │ Device    ├─────────┤  Time     │                │
│                │ Context   │         │ Context   │                │
│                │           │         │           │                │
│                └───────────┘         └───────────┘                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Knowledge Visualization Implementation

```typescript
/**
 * Interactive knowledge graph visualization component for commitment management
 * Designed to show relationships between commitments, contexts, and other entities
 */
class CommitmentKnowledgeVisualizer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private graph: any; // Force-directed graph layout
  private nodes: KnowledgeNode[] = [];
  private links: KnowledgeLink[] = [];
  private selectedNode: KnowledgeNode | null = null;
  
  constructor(canvasId: string) {
    // Initialize canvas
    this.canvas = document.getElementById(canvasId) as HTMLCanvasElement;
    this.ctx = this.canvas.getContext('2d')!;
    
    // Set up event listeners
    this.setupInteractions();
    
    // Set up force-directed graph
    this.initializeGraph();
  }
  
  /**
   * Add nodes and links to the knowledge graph
   */
  public loadData(nodes: KnowledgeNode[], links: KnowledgeLink[]): void {
    this.nodes = nodes;
    this.links = links;
    this.updateGraph();
  }
  
  /**
   * Update the visualization with new data
   */
  public updateGraph(): void {
    // Clear existing graph
    this.graph.nodes([]);
    this.graph.links([]);
    
    // Add nodes and links
    this.graph.nodes(this.nodes);
    this.graph.links(this.links);
    
    // Start simulation
    this.graph.start();
    this.renderGraph();
  }
  
  /**
   * Highlight nodes and connections related to a commitment
   */
  public highlightCommitmentContext(commitmentId: string): void {
    // Find the commitment node
    const commitmentNode = this.nodes.find(node => 
      node.id === commitmentId && node.type === 'commitment'
    );
    
    if (!commitmentNode) return;
    
    // Find all directly connected nodes
    const connectedNodeIds = new Set<string>();
    for (const link of this.links) {
      if (link.source === commitmentId) {
        connectedNodeIds.add(link.target);
      } else if (link.target === commitmentId) {
        connectedNodeIds.add(link.source);
      }
    }
    
    // Update visual properties for highlighting
    for (const node of this.nodes) {
      if (node.id === commitmentId) {
        node.highlighted = true;
        node.radius = 15; // Larger radius for selected node
      } else if (connectedNodeIds.has(node.id)) {
        node.highlighted = true;
        node.radius = 10; // Medium radius for connected nodes
      } else {
        node.highlighted = false;
        node.radius = 5; // Default radius
      }
    }
    
    // Update link highlighting
    for (const link of this.links) {
      link.highlighted = 
        link.source === commitmentId || 
        link.target === commitmentId;
    }
    
    this.renderGraph();
  }
  
  /**
   * Export the current visualization as an image
   */
  public exportAsImage(): string {
    return this.canvas.toDataURL('image/png');
  }
  
  /**
   * Generate a report of connections in the graph
   */
  public generateReport(): KnowledgeReport {
    const nodeTypes = new Map<string, number>();
    const connectionTypes = new Map<string, number>();
    
    // Count node types
    for (const node of this.nodes) {
      const count = nodeTypes.get(node.type) || 0;
      nodeTypes.set(node.type, count + 1);
    }
    
    // Count connection types
    for (const link of this.links) {
      const count = connectionTypes.get(link.type) || 0;
      connectionTypes.set(link.type, count + 1);
    }
    
    // Find most connected nodes
    const nodeConnections = new Map<string, number>();
    for (const link of this.links) {
      const sourceCount = nodeConnections.get(link.source) || 0;
      nodeConnections.set(link.source, sourceCount + 1);
      
      const targetCount = nodeConnections.get(link.target) || 0;
      nodeConnections.set(link.target, targetCount + 1);
    }
    
    const sortedByConnections = Array.from(nodeConnections.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5); // Top 5
    
    const mostConnectedNodes = sortedByConnections.map(([id, count]) => {
      const node = this.nodes.find(n => n.id === id);
      return {
        id,
        label: node?.label || id,
        type: node?.type || 'unknown',
        connections: count
      };
    });
    
    return {
      totalNodes: this.nodes.length,
      totalConnections: this.links.length,
      nodeTypes: Object.fromEntries(nodeTypes),
      connectionTypes: Object.fromEntries(connectionTypes),
      mostConnectedNodes
    };
  }
  
  // Rendering and interaction methods omitted for brevity
}

/**
 * Usage example:
 * 
 * const visualizer = new CommitmentKnowledgeVisualizer('knowledge-canvas');
 * 
 * // Sample data
 * const nodes = [
 *   { id: 'comm1', label: 'Call Client', type: 'commitment', x: 100, y: 100 },
 *   { id: 'loc1', label: 'Office', type: 'location', x: 200, y: 50 },
 *   { id: 'time1', label: 'Morning', type: 'time', x: 300, y: 150 }
 * ];
 * 
 * const links = [
 *   { source: 'comm1', target: 'loc1', type: 'best_at' },
 *   { source: 'comm1', target: 'time1', type: 'scheduled_for' }
 * ];
 * 
 * visualizer.loadData(nodes, links);
 * visualizer.highlightCommitmentContext('comm1');
 */
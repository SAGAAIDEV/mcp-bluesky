# Epic Development Plan: MCP Bluesky Server

**Document Control**

- Version: 2.0.0
- Date: 2024-12-19
- Status: Draft
- Product Owner: Senior Software Architect
- Technical Lead: Backend Development Team Lead
- Epic Owner: Development Team Lead

## Epic Overview

**Epic Title:** MCP Bluesky Server  
**Epic Description:** Build a Model Context Protocol (MCP) compliant server that enables AI agents to seamlessly interact with the Bluesky social media platform through standardized interfaces.

**Epic Objectives:**
- Enable AI agents to authenticate and configure Bluesky access
- Provide comprehensive content publishing capabilities (text, images, videos)
- Support social interaction through replies and conversation management
- Enable content discovery through hashtag search and feed reading
- Maintain full MCP protocol compliance for seamless AI agent integration

**Epic Success Criteria:**
- All 9 user stories completed and accepted
- MCP protocol compliance verified through automated testing
- Security requirements met with secure credential management
- Performance targets achieved (<2s for text, <30s for media)
- Production-ready PyPI package with comprehensive documentation

**Epic Timeline:** 10 weeks (5 sprints × 2 weeks)  
**Total Story Points:** 105 points  
**Team Velocity:** 21 story points per sprint  

---

## User Stories

### User Story 1: MCP Server Initialization and Discovery
**Story ID:** BS-001  
**Story Points:** 8 SP  
**Priority:** Highest  
**Sprint:** Sprint 1

**Description:** As an MCP client application or AI agent, I need the Bluesky MCP server to initialize with proper protocol compliance and tool registration, so that I can discover and utilize Bluesky social media capabilities through standardized MCP interfaces.

**Acceptance Criteria:**
- AC1: MCP protocol handshake with server capabilities and available tools
- AC2: tool registration for all 8 Bluesky tools
- AC3: Health check endpoint with Bluesky API connectivity status
- AC4: Graceful error handling for initialization failures
- AC5: tool registry in a ai assited code editor from it's mcp.json file.

**Task Breakdown:**

**Task 1.1: Project Structure and Setup**
- Create project template using cookiecutter-pypackage
- Set up development environment with poetry
- Configure pre-commit hooks and linting
- Add initial project documentation structure
- **Effort:** 2 SP

**Task 1.2: MCP Protocol Infrastructure Setup**
- Implement MCP server using Python `mcp` library
- Configure FastMCP server 
- Implement protocol handshake and capability advertisement
- **Effort:** 3 SP

**Task 1.3: Tool Registration Framework**
- Implement automatic tool discovery using `@mcp.tool` decorator
- Register all 8 Bluesky tools with proper schemas
- Set up tool name inference from function names
- Generate tool descriptions from docstrings
- **Effort:** 2 SP

**Task 1.4: Health Check and Status Endpoints**
- Implement server health check endpoint
- Add Bluesky API connectivity validation
- Create server status reporting with detailed diagnostics
- Add configuration validation checks
- **Effort:** 2 SP

**Task 1.5: Error Handling and Logging**
- Implement comprehensive error handling framework
- Set up structured logging with loguru
- Add MCP-compliant error responses
- Implement graceful shutdown procedures
- **Effort:** 1 SP

---

### User Story 2: Bluesky Authentication and Configuration Management
**Story ID:** BS-002  
**Story Points:** 13 SP  
**Priority:** Highest  
**Sprint:** Sprint 1

**Description:** As a developer setting up the Bluesky MCP server, I want to authenticate with Bluesky using my credentials and generate proper configuration files, so that I can securely integrate the MCP server into my AI agent workflow.

**Acceptance Criteria:**
- AC1: Interactive configuration initialization with `mcp-bluesky --init` 
- AC2: Multi-account YAML configuration support
- AC3: MCP JSON integration instructions
- AC4: Configuration validation commands
- AC5: Account management commands
- AC6: Configuration display with masked credentials
- AC7: Configuration cleanup operations
- AC8: Connectivity testing for all accounts

**Task Breakdown:**

**Task 2.1: CLI Framework Setup**
- Implement Google Fire CLI framework
- Create main CLI class with command structure
- Set up command entry points and help system
- Add version and debug options
- **Effort:** 2 SP

**Task 2.2: Configuration Initialization**
- Implement `--init` command for configuration creation
- Create platform-specific configuration directories
- Generate YAML configuration templates
- Add environment variable placeholder support
- **Effort:** 3 SP

**Task 2.3: Multi-Account Configuration**
- Design multi-account YAML schema
- Implement account alias management
- Add default account selection logic
- Support multiple Bluesky instance configurations
- Store API key
- **Effort:** 3 SP



**Task 2.5: Configuration Management Commands**
- Implement `config show` with credential masking
- Add `config validate --account` to check that blue sky api key works with account
- Create `config clean` and `config reset` commands
- Add connectivity testing with user profile retrieval
- **Effort:** 2 SP

---

### User Story 3: Text Post Creation via MCP Tool
**Story ID:** BS-003  
**Story Points:** 8 SP  
**Priority:** High  
**Sprint:** Sprint 2

**Description:** As an AI agent, I want to create text posts on Bluesky through the MCP `bluesky_post_text` tool, so that I can automatically publish content to the platform.

**Acceptance Criteria:**
- AC1: Basic text posting with post ID and URL return
- AC2: Character limit validation (300 characters)
- AC3: Rich text support (mentions, hashtags)
- AC4: Rate limiting and error handling
- AC5: Post confirmation with metadata
- AC6: Multi-account support

**Task Breakdown:**

**Task 3.1: AT Protocol Text Posting**
- Implement AT Protocol client integration
- Add text post creation via `com.atproto.repo.createRecord`
- Set up proper AT URI handling and post validation
- Implement post metadata extraction
- **Effort:** 3 SP

**Task 3.2: Input Validation and Rich Text**
- Add character limit validation (300 chars)
- Implement mention parsing and linking (@user.bsky.social)
- Add hashtag detection and formatting (#hashtag)
- Create URL detection and link embedding
- **Effort:** 2 SP

**Task 3.3: MCP Tool Implementation**
- Create `bluesky_post_text` MCP tool with proper schema
- Add multi-account support with account parameter
- Implement response formatting with post metadata
- Add comprehensive error handling and validation
- **Effort:** 2 SP

**Task 3.4: Error Handling and Rate Limiting**
- Implement rate limiting detection and backoff
- Add comprehensive error responses with troubleshooting
- Create retry logic for transient failures
- Add timeout handling for API calls
- **Effort:** 1 SP

**Task 3.5: CLI Interface Implementation**
- Create `post text` command with interactive mode


- Add account selection via `--account` flag
- Create post confirmation prompt
- **Effort:** 3 SP

**Task 3.6: CLI Documentation and Help**
- Add comprehensive command help text
- Create usage examples and documentation
- Implement interactive mode tutorial
- Add command completion support
- **Effort:** 2 SP

---

### User Story 4: Image Post Creation via MCP Tool
**Story ID:** BS-004  
**Story Points:** 13 SP  
**Priority:** High  
**Sprint:** Sprint 2

**Description:** As an AI agent or CLI user, I want to create posts with images and optional text on Bluesky through both the MCP `bluesky_post_image` tool and CLI interface, so that I can publish visual content with descriptive captions.

**Acceptance Criteria:**
- AC1: Image upload and posting with blob storage
- AC2: Format validation (JPEG, PNG, WebP)
- AC3: Automatic resizing and compression for 1MB limit
- AC4: Alt-text accessibility support
- AC5: Combined text and image posting
- AC6: Multi-account support
- AC7: CLI interface with interactive and non-interactive modes

**Task Breakdown:**

**Task 4.1: Image Processing Pipeline**
- Implement image format validation (JPEG, PNG, WebP)
- Add automatic image resizing and compression using Pillow
- Create image optimization while maintaining quality
- Add image metadata extraction and validation
- **Effort:** 4 SP

**Task 4.2: Blob Storage Integration**
- Implement AT Protocol blob upload via `com.atproto.repo.uploadBlob`
- Add progress tracking for large image uploads
- Create blob reference management and cleanup
- Implement upload error handling and retry logic
- **Effort:** 3 SP

**Task 4.3: MCP Tool Implementation**
- Create `bluesky_post_image` MCP tool with schema
- Add file path processing and validation
- Implement alt-text and accessibility features
- Add multi-account support and response formatting
- **Effort:** 2 SP

**Task 4.4: CLI Interface Implementation**
- Create `post image` command with interactive mode
- Add `--text` and `--image-path` flags for non-interactive use
- Implement account selection via `--account` flag
- Add post preview and confirmation prompt
- Create progress indicators for upload status
- **Effort:** 2 SP

**Task 4.5: Combined Post Creation**
- Integrate image blob with text post creation
- Add combined text and image validation
- Implement post preview with text and image
- Create comprehensive error handling for media failures
- **Effort:** 2 SP

---

### User Story 5: Video Post Creation via MCP Tool
**Story ID:** BS-005  
**Story Points:** 21 SP  
**Priority:** Medium  
**Sprint:** Sprint 4

**Description:** As an AI agent or CLI user, I want to create posts with videos on Bluesky through the MCP `bluesky_post_video` tool or CLI command, so that I can publish dynamic video content with optional text descriptions.

**Acceptance Criteria:**
- AC1: Video upload and posting with blob storage
- AC2: Format validation (MP4/H.264, WebM)
- AC3: Duration (2 min) and size (50MB) limit enforcement
- AC4: Automatic thumbnail generation
- AC5: Processing status updates
- AC6: Multi-account support
- AC7: CLI interface with interactive and non-interactive modes
- AC8: Command line usage: `bluesky post video --text "Description" --video-path /path/to/video.mp4`

**Task Breakdown:**

**Task 5.1: Video Processing Infrastructure**
- Implement video format validation using python-ffmpeg
- Add duration and file size limit checking
- Create video metadata extraction and analysis
- Set up efficient video file handling and streaming
- **Effort:** 6 SP

**Task 5.2: Video Blob Upload System**
- Implement large file upload with progress tracking
- Add chunked upload support for 50MB files
- Create upload status monitoring and reporting
- Implement robust error handling and recovery
- **Effort:** 5 SP

**Task 5.3: Thumbnail Generation**
- Implement automatic thumbnail creation from first frame
- Add custom timestamp thumbnail generation
- Create thumbnail optimization and compression
- Add thumbnail upload and blob management
- **Effort:** 4 SP

**Task 5.4: Video MCP Tool**
- Create `bluesky_post_video` MCP tool with comprehensive schema
- Add video processing status updates
- Implement multi-account support and validation
- Create video post creation with thumbnail embedding
- **Effort:** 4 SP

**Task 5.5: Async Processing and Status**
- Implement non-blocking video processing
- Add processing status polling and updates
- Create timeout handling for long operations
- Implement memory management for large files
- **Effort:** 2 SP

**Task 5.6: CLI Interface Implementation**
- Create `post video` command with interactive mode
- Add `--text` and `--video-path` flags for non-interactive use
- Implement account selection via `--account` flag
- Add post preview and confirmation prompt
- Create progress indicators for upload and processing status
- Add command line help and usage documentation
- Implement argument parsing and validation
- **Effort:** 2 SP

---

### User Story 6: Reply to Posts via MCP Tool
**Story ID:** BS-006  
**Story Points:** 8 SP  
**Priority:** High  
**Sprint:** Sprint 3

**Description:** As an AI agent, I want to reply to existing Bluesky posts through the MCP `bluesky_reply` tool, so that I can engage in conversations.

**Acceptance Criteria:**
- AC1: Basic reply functionality with thread linking
- AC2: Reply with media support
- AC3: Post URI validation
- AC4: Multi-account reply support

**Task Breakdown:**

**Task 6.1: Thread and Reply Infrastructure**
- Implement AT Protocol thread relationship handling
- Add parent post validation and existence checking
- Create proper reply chain linking and threading
- Set up conversation context management
- **Effort:** 3 SP

**Task 6.2: Reply Creation Logic**
- Implement reply post creation with parent references
- Add thread metadata and relationship establishment
- Create notification triggering for parent authors
- Add reply validation and error handling
- **Effort:** 2 SP

**Task 6.3: Media Reply Support**
- Extend reply functionality to support image attachments
- Integrate existing image processing pipeline
- Add media validation for reply context
- Implement combined text and media reply creation
- **Effort:** 2 SP

**Task 6.4: MCP Tool Implementation**
- Create `bluesky_reply` MCP tool with proper schema
- Add multi-account support for replies
- Implement comprehensive error handling
- Add reply confirmation and metadata response
- **Effort:** 1 SP

---

### User Story 7: Get Replies and Comments via MCP Tool
**Story ID:** BS-007  
**Story Points:** 13 SP  
**Priority:** High  
**Sprint:** Sprint 3

**Description:** As an AI agent, I want to retrieve replies and comments from Bluesky posts through the MCP `bluesky_get_replies` tool, so that I can analyze conversations.

**Acceptance Criteria:**
- AC1: Paginated reply retrieval with proper structure
- AC2: Multi-level thread support (up to 10 levels)
- AC3: Sort options and filtering
- AC4: Author information and metadata
- AC5: Multi-account support

**Task Breakdown:**

**Task 7.1: Thread Traversal Engine**
- Implement recursive thread traversal algorithm
- Add configurable depth limiting (default: 10 levels)
- Create efficient caching for large conversation trees
- Add circular reference detection and prevention
- **Effort:** 5 SP

**Task 7.2: Reply Retrieval System**
- Implement AT Protocol reply fetching via thread endpoints
- Add paginated retrieval with cursor-based navigation
- Create reply sorting by time and engagement
- Add author information and metadata extraction
- **Effort:** 4 SP

**Task 7.3: Thread Structure Management**
- Create nested thread structure representation
- Add thread visualization and hierarchy tracking
- Implement thread metadata and statistics
- Add memory optimization for deep threads
- **Effort:** 2 SP

**Task 7.4: MCP Tool Implementation**
- Create `bluesky_get_replies` MCP tool with comprehensive schema
- Add multi-account support and filtering options
- Implement response formatting with thread structure
- Add error handling for missing posts and permissions
- **Effort:** 2 SP

---

### User Story 8: Search Hashtags via MCP Tool and CLI
**Story ID:** BS-008  
**Story Points:** 16 SP  
**Priority:** Medium  
**Sprint:** Sprint 5

**Description:** As an AI agent or CLI user, I want to search for hashtags and topics on Bluesky through both the MCP `bluesky_search_hashtags` tool and CLI interface, so that I can discover trending content through multiple interfaces.

**Acceptance Criteria:**
- AC1: Single and multiple hashtag search
- AC2: Advanced filtering (time range, engagement)
- AC3: Multiple hashtag search with operators
- AC4: Paginated search results
- AC5: CLI interface with interactive and non-interactive modes
- AC6: Rich terminal output with formatted results
- AC7: Search history and saved searches

**Task Breakdown:**

**Task 8.1: Search Infrastructure**
- Implement AT Protocol search functionality
- Add hashtag parsing and normalization
- Create search query construction and optimization
- Set up search result caching and performance optimization
- **Effort:** 4 SP

**Task 8.2: Advanced Search Features**
- Add time-based filtering (1h to 30d ranges)
- Implement engagement filtering (minimum likes/replies)
- Create multiple hashtag search with AND/OR operators
- Add search result ranking and relevance scoring
- **Effort:** 4 SP

**Task 8.3: Search Result Processing**
- Implement paginated search result handling
- Add search metadata and statistics
- Create result formatting with engagement metrics
- Add search performance monitoring and optimization
- **Effort:** 3 SP

**Task 8.4: MCP Tool Implementation**
- Create `bluesky_search_hashtags` MCP tool with advanced schema
- Add comprehensive filtering and pagination support
- Implement multi-account search capabilities
- Add error handling for search failures and rate limits
- **Effort:** 2 SP

**Task 8.5: CLI Interface Implementation**
- Create `search hashtags` command with interactive mode
- Add rich terminal output using rich library
- Implement search history and saved searches
- Add command completion and help system
- **Effort:** 3 SP

---

### User Story 9: Get Feed Content via MCP Tool
**Story ID:** BS-009  
**Story Points:** 13 SP  
**Priority:** Medium  
**Sprint:** Sprint 5

**Description:** As an AI agent, I want to retrieve feed content from Bluesky through the MCP `bluesky_get_feed` tool and persist it to a database or JSON file, so that I can monitor timelines, discover content, and maintain historical records. If a db is chosen, connection credentials, and schema map should be applied to send the request directly to a db.

**Acceptance Criteria:**
- AC1: Home, discover, and following feed retrieval
- AC2: Paginated feed loading
- AC3: Multi-account feed access
- AC4: Content type filtering
- AC5: SQLite database persistence with configurable schema mapping, db connection
- AC6: JSON file export option
- AC7: Data transformation and schema mapping support
- AC8: Incremental updates and change tracking

**Task Breakdown:**

**Task 9.1: Feed Retrieval System**
- Implement AT Protocol feed endpoints access
- Add support for home, discover, and following feeds
- Create feed pagination with cursor management
- Set up feed caching and refresh optimization
- **Effort:** 3 SP

**Task 9.2: Feed Processing and Filtering**
- Add content type filtering (text, image, video)
- Implement feed metadata extraction
- Create engagement data processing
- Add feed performance optimization
- **Effort:** 2 SP

**Task 9.3: Multi-Account Feed Management**
- Implement account-specific feed retrieval
- Add feed aggregation across multiple accounts
- Create account-based feed caching
- Add feed synchronization and updates
- **Effort:** 2 SP

**Task 9.4: Database Integration**
- Implement SQLite database connection management
- Create configurable schema mapping system
- Add data transformation layer for Bluesky to DB mapping
- Implement incremental update tracking
- **Effort:** 3 SP

**Task 9.5: JSON Export System**
- Create JSON file export functionality
- Add configurable export formats and schemas
- Implement incremental JSON updates
- Add export compression and optimization
- **Effort:** 2 SP

**Task 9.6: MCP Tool Implementation**
- Create `bluesky_get_feed` MCP tool with comprehensive schema
- Add pagination and filtering support
- Implement multi-account feed access
- Add database and JSON export options
- Include schema mapping configuration
- Add error handling and performance monitoring
- **Effort:** 1 SP

**Database Schema Example:**

## Sprint Organization

### Sprint 1: Foundation Sprint (Weeks 1-2)
**Sprint Goal:** Establish core MCP server infrastructure and secure authentication  
**Sprint Points:** 21 SP

**Included Stories:**
- BS-001: MCP Server Initialization and Discovery (8 SP)
- BS-002: Bluesky Authentication and Configuration Management (13 SP)

**Key Deliverables:**
- Functional MCP server with tool registration
- Complete CLI configuration interface
- Multi-account authentication system
- Comprehensive test suite and documentation

### Sprint 2: Core Content Sprint (Weeks 3-4)
**Sprint Goal:** Implement essential content publishing capabilities  
**Sprint Points:** 21 SP

**Included Stories:**
- BS-003: Text Post Creation via MCP Tool (8 SP)
- BS-004: Image Post Creation via MCP Tool (13 SP)

**Key Deliverables:**
- Text and image posting functionality
- Rich content support (mentions, hashtags)
- Media processing pipeline
- Multi-account posting capabilities

### Sprint 3: Interaction Sprint (Weeks 5-6)
**Sprint Goal:** Enable conversation participation and social interaction  
**Sprint Points:** 21 SP

**Included Stories:**
- BS-006: Reply to Posts via MCP Tool (8 SP)
- BS-007: Get Replies and Comments via MCP Tool (13 SP)

**Key Deliverables:**
- Reply creation and threading
- Conversation retrieval and analysis
- Multi-level thread support
- Social engagement capabilities

### Sprint 4: Advanced Features Sprint (Weeks 7-8)
**Sprint Goal:** Implement advanced multimedia capabilities  
**Sprint Points:** 21 SP

**Included Stories:**
- BS-005: Video Post Creation via MCP Tool (21 SP)

**Key Deliverables:**
- Video upload and processing
- Thumbnail generation
- Large file handling
- Advanced media capabilities

### Sprint 5: Discovery Sprint (Weeks 9-10)
**Sprint Goal:** Complete content discovery and feed management capabilities  
**Sprint Points:** 21 SP

**Included Stories:**
- BS-008: Search Hashtags via MCP Tool (13 SP)
- BS-009: Get Feed Content via MCP Tool (8 SP)

**Key Deliverables:**
- Hashtag search and discovery
- Feed reading and monitoring
- Content analysis capabilities
- Complete feature set

---

## Success Metrics and Completion Criteria

### Epic Success Metrics
- **Functional Completeness:** All 9 user stories completed and accepted
- **Performance Standards:** <2s for text posts, <30s for media uploads
- **Security Compliance:** Secure authentication and credential management
- **MCP Protocol Compliance:** 100% specification adherence
- **Quality Gates:** >90% test coverage, zero critical vulnerabilities

### Definition of Done (Epic Level)
- [ ] All user stories meet acceptance criteria
- [ ] Comprehensive test suite with >90% coverage
- [ ] Security scan passes with no critical issues
- [ ] Performance benchmarks meet targets
- [ ] Production-ready PyPI package published
- [ ] Complete documentation and setup guides
- [ ] MCP protocol compliance verified

### Risk Management
- **Sprint 1:** Foundation dependencies and MCP integration complexity
- **Sprint 2:** Image processing performance and media handling
- **Sprint 3:** Thread traversal complexity and conversation state
- **Sprint 4:** Video processing resource requirements and performance
- **Sprint 5:** Search performance and feed caching optimization

---

*This Epic Development Plan provides the comprehensive roadmap for implementing the MCP Bluesky Server through user story decomposition into actionable tasks organized across 5 focused sprints, ensuring incremental delivery of a production-ready system.* 
# Development Strategy for Bluesky MCP Server

**Document Version:** 1.0
**Last Updated:** July 2025
**Author:** Development Team

## Executive Summary

This document outlines the recommended development strategy for the Bluesky MCP server project, building upon the existing prototype fork. The strategy prioritizes safety, compliance, and maintainability while ensuring efficient parallel development and risk mitigation.

## Current State Assessment

### ✅ What's Already Implemented
- **Core MCP Infrastructure**: FastMCP framework with tool registration
- **Basic Authentication**: Environment variable-based auth system
- **Complete Tool Set**: All documented user stories (BS-001 to BS-009) are functionally implemented
- **Media Support**: Image and video posting capabilities
- **Social Features**: Following, liking, reposting, and basic feed access
- **Test Coverage**: Comprehensive test suite for core functionality

### ❌ Critical Missing Components
- **Input Validation**: No character limits, format validation, or sanitization
- **Rate Limiting**: No API throttling or request management
- **Error Handling**: Inconsistent error responses and logging
- **Media Validation**: No file size limits or format enforcement
- **Configuration Management**: No YAML/CLI configuration system
- **Production Logging**: No structured logging or monitoring

## Development Strategy Overview

### 🎯 Core Principles

1. **Safety First**: Prevent system failures and data corruption
2. **Compliance Critical**: Avoid Bluesky API violations and bans
3. **Incremental Development**: Maintain working functionality throughout
4. **Sequential Focus**: Complete each phase thoroughly before advancing
5. **Test-Driven**: Comprehensive testing at each phase

### 👤 Single Developer + AI Assistance

**AI Acceleration Areas:**
- **Boilerplate Code**: AI excels at generating standard patterns, configs, tests
- **Documentation**: AI can help with docstrings, README updates, type hints
- **Refactoring**: AI can help reorganize code structure efficiently
- **Test Generation**: AI can create comprehensive test cases quickly

**AI Limitations & Correction Overhead:**
- **Complex Logic**: AI often makes errors in business logic and edge cases
- **Integration Points**: AI struggles with cross-module dependencies
- **Error Debugging**: AI-generated bugs can be subtle and hard to track
- **Context Loss**: AI may not maintain full project context across sessions

**Development Approach:**
- **Use AI for**: Standard implementations, boilerplate, documentation, tests
- **Human Focus**: Architecture decisions, business logic, debugging, integration
- **Correction Budget**: 20-30% extra time for reviewing and fixing AI code
- **Iterative Validation**: Test AI output immediately and frequently

### 📊 Risk-Based Prioritization

**CRITICAL RISKS (Project Killers)**:
- Rate limiting violations → API ban
- Input validation failures → Data corruption
- Unhandled exceptions → System crashes

**HIGH RISKS (Major Delays)**:
- Poor code organization → Development bottlenecks
- Missing media validation → User experience issues

**MEDIUM RISKS (Quality Issues)**:
- No configuration management → Deployment difficulties
- Performance problems → User dissatisfaction

## Phase 0: Project Foundation (Pre-Development)

**Duration:** 1-2 days
**Priority:** CRITICAL
**Jira Stories:** BS-000 (MCP-93)

### Objectives
- Organize codebase for efficient development
- Set up infrastructure for future phases
- Enable parallel development

### Tasks

#### Task 0.1: Code Structure Refactoring (MCP-94)
**Effort:** 3 SP

**Proposed Directory Structure:**
```
mcp-bluesky/
├── server.py                 # Main MCP server setup only
├── src/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_tools.py     # check_auth_status
│   ├── posts/
│   │   ├── __init__.py
│   │   ├── creation.py       # send_post, send_image, send_video
│   │   ├── interaction.py    # like_post, unlike_post, repost
│   │   └── retrieval.py      # get_post, get_posts, get_timeline
│   ├── users/
│   │   ├── __init__.py
│   │   ├── profiles.py       # get_profile, resolve_handle
│   │   ├── follows.py        # follow_user, unfollow_user, get_follows
│   │   └── moderation.py     # mute_user, unmute_user
│   ├── feeds/
│   │   ├── __init__.py
│   │   └── timeline.py       # get_author_feed, get_post_thread
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validation.py     # Input validation framework
│   │   ├── rate_limiting.py  # Rate limiting framework
│   │   └── media_utils.py    # Media processing helpers
│   └── config/
│       ├── __init__.py
│       └── settings.py       # Configuration management
├── tests/
│   ├── unit/                 # Unit tests per module
│   └── integration/          # Integration tests
└── docs/
```

**Implementation Steps:**
1. Create new directory structure
2. Move tools to appropriate modules by category
3. Update imports in `server.py`
4. Verify all tools still work correctly
5. Update documentation

**Quality Gates:**
- All existing tests pass
- Tool discovery functions correctly
- No functionality changes

#### Task 0.2: Infrastructure Module Setup (MCP-95)
**Effort:** 2 SP

**Framework Creation:**
```python
# utils/validation.py - Ready for Phase 1
def validate_text_length(text: str, max_length: int = 300) -> None:
    """Validate text length - to be implemented in Phase 1"""
    pass

# utils/rate_limiting.py - Ready for Phase 2
class RateLimiter:
    """Rate limiting framework - to be implemented in Phase 2"""
    pass

# utils/media_utils.py - Ready for Phase 3
def validate_media_format(data: bytes, allowed_formats: list) -> bool:
    """Media validation - to be implemented in Phase 3"""
    pass

# config/settings.py - Ready for Phase 4
class Settings:
    """Configuration management - to be implemented in Phase 4"""
    pass
```

## Phase 1: Foundation & Safety (Sprint 1)

**Duration:** 1-2 weeks
**Priority:** HIGHEST
**Focus:** Prevent system failures and data corruption

### 1.1 Input Validation & Sanitization
**Jira Stories:** BS-00A (Input Validation & Safety Framework)

**Implementation Priority:**
1. **Text Validation** (300 character limits)
2. **File Validation** (size, format, MIME type)
3. **Parameter Sanitization** (all tool endpoints)
4. **Encoding Validation** (UTF-8, special characters)

**Example Implementation:**
```python
# utils/validation.py
def validate_text_length(text: str, max_length: int = 300) -> None:
    if len(text) > max_length:
        raise ValueError(f"Text exceeds {max_length} character limit")

def validate_file_size(data: bytes, max_size: int = 1048576) -> None:  # 1MB
    if len(data) > max_size:
        raise ValueError(f"File size exceeds {max_size} bytes")

# Apply to tools
@mcp.tool()
async def send_post(text: str) -> dict:
    validate_text_length(text)  # Add validation
    # ... existing implementation
```

### 1.2 Comprehensive Error Handling
**Jira Stories:** BS-00C (Error Handling & Logging System)

**Structured Error Responses:**
```python
class BlueskyError(Exception):
    def __init__(self, message: str, error_code: str, http_status: int = 400):
        self.message = message
        self.error_code = error_code
        self.http_status = http_status

def handle_tool_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BlueskyError as e:
            return {"status": "error", "message": e.message, "code": e.error_code}
        except Exception as e:
            return {"status": "error", "message": "Internal server error", "code": "INTERNAL_ERROR"}
    return wrapper
```

### 1.3 Logging Infrastructure
**Jira Stories:** BS-00C (Error Handling & Logging System)

**Structured Logging with Loguru:**
```python
import loguru

logger.add("logs/bluesky_mcp.log", rotation="1 day", retention="30 days")

@logger.catch
@mcp.tool()
async def send_post(text: str) -> dict:
    logger.info(f"Attempting to send post: {len(text)} characters")
    # ... implementation
    logger.info(f"Post sent successfully: {result['uri']}")
```

## Phase 2: API Compliance (Sprint 1-2)

**Duration:** 1-2 weeks
**Priority:** HIGHEST
**Focus:** Prevent rate limiting and API violations

### 2.1 Rate Limiting Implementation
**Jira Stories:** BS-00B (Basic Rate Limiting & API Safety - Prototype)

**Multi-Tier Rate Limiting:**
```python
# utils/rate_limiting.py
class BlueskyRateLimiter:
    def __init__(self):
        self.limits = {
            'posts': {'requests': 30, 'window': 60},      # 30 posts/minute
            'follows': {'requests': 60, 'window': 60},     # 60 follows/minute
            'general': {'requests': 120, 'window': 60}     # 120 general/minute
        }

    async def check_limit(self, endpoint: str) -> bool:
        # Implementation with Redis/memory store
        pass

    def exponential_backoff(self, attempt: int) -> float:
        return min(2 ** attempt, 300)  # Max 5 minutes
```

**Rate Limiting Decorator:**
```python
@rate_limit(category='posts', requests_per_minute=30)
@mcp.tool()
async def send_post(text: str) -> dict:
    # ... implementation
```

### 2.2 Request Queue Management
**Jira Stories:** Deferred to Phase 4 (Production Enhancement) - prototype uses simple rate limiting

**Queue Implementation:**
```python
import asyncio
from collections import deque

class RequestQueue:
    def __init__(self, max_concurrent: int = 5):
        self.queue = deque()
        self.active = 0
        self.max_concurrent = max_concurrent

    async def execute_with_queue(self, func, *args, **kwargs):
        await self.wait_for_slot()
        try:
            self.active += 1
            return await func(*args, **kwargs)
        finally:
            self.active -= 1
```

### 2.3 Retry Logic with Exponential Backoff
**Jira Stories:** Deferred to Phase 4 (Production Enhancement) - basic error handling in BS-00C

**Smart Retry Implementation:**
```python
async def retry_with_backoff(func, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = min(2 ** attempt, 300)
            await asyncio.sleep(wait_time)
        except PermanentError:
            raise  # Don't retry permanent failures
```

## Phase 3: Media & Content Enhancement (Sprint 2)

**Duration:** 2-3 weeks
**Priority:** HIGH
**Focus:** Reliable media handling and content processing

### 3.1 Advanced Media Handling
**Jira Stories:** TBD

**Media Processing Pipeline:**
```python
# utils/media_utils.py
import PIL.Image
import ffmpeg

class MediaProcessor:
    def __init__(self):
        self.max_size = 1048576  # 1MB
        self.allowed_image_formats = ['JPEG', 'PNG', 'WebP']
        self.allowed_video_formats = ['MP4', 'MOV']

    async def process_image(self, data: bytes) -> bytes:
        # Validate, compress, convert if needed
        image = PIL.Image.open(io.BytesIO(data))

        # Auto-convert to WebP if too large
        if len(data) > self.max_size:
            return self.compress_to_webp(image)

        return data

    async def process_video(self, data: bytes) -> bytes:
        # Validate format, size, duration
        # Compress if needed
        pass
```

### 3.2 Content Processing
**Jira Stories:** TBD

**Rich Text Features:**
```python
class ContentProcessor:
    def __init__(self):
        self.hashtag_pattern = re.compile(r'#\w+')
        self.mention_pattern = re.compile(r'@[\w.]+')
        self.url_pattern = re.compile(r'https?://[^\s]+')

    def extract_facets(self, text: str) -> list:
        facets = []
        # Extract hashtags, mentions, URLs
        # Create AT Protocol facet objects
        return facets

    def generate_link_preview(self, url: str) -> dict:
        # Fetch metadata, create preview
        pass
```

## Phase 4: Configuration & Deployment (Sprint 2-3)

**Duration:** 1-2 weeks
**Priority:** MEDIUM
**Focus:** Production deployment capabilities

### 4.1 Configuration Management
**Jira Stories:** TBD

**YAML Configuration Support:**
```yaml
# bluesky_config.yaml
authentication:
  identifier: "${BLUESKY_IDENTIFIER}"
  app_password: "${BLUESKY_APP_PASSWORD}"
  service_url: "https://bsky.social"

rate_limits:
  posts_per_minute: 30
  follows_per_minute: 60
  general_per_minute: 120

media:
  max_file_size: 1048576
  allowed_image_formats: ["JPEG", "PNG", "WebP"]
  auto_compress: true

logging:
  level: "INFO"
  file: "logs/bluesky_mcp.log"
  rotation: "1 day"
```

### 4.2 CLI Interface
**Jira Stories:** TBD

**Command Line Tools:**
```python
# cli.py
import click

@click.group()
def cli():
    """Bluesky MCP Server CLI"""
    pass

@cli.command()
@click.option('--config', help='Configuration file path')
def init(config):
    """Initialize configuration"""
    create_default_config(config)

@cli.command()
def validate():
    """Validate configuration"""
    check_config_validity()

@cli.command()
@click.option('--port', default=8000)
def serve(port):
    """Start the MCP server"""
    start_server(port)
```

### 4.3 Docker & Deployment
**Jira Stories:** TBD

**Enhanced Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["python", "server.py"]
```

## Phase 5: Performance & Polish (Sprint 3)

**Duration:** 1-2 weeks
**Priority:** LOW
**Focus:** Optimization and developer experience

### 5.1 Performance Optimization
**Jira Stories:** TBD

**Caching Strategy:**
```python
import redis

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis()

    async def cache_user_profile(self, handle: str, profile: dict):
        key = f"profile:{handle}"
        self.redis.setex(key, 300, json.dumps(profile))  # 5 min cache

    async def get_cached_profile(self, handle: str) -> dict:
        key = f"profile:{handle}"
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None
```

### 5.2 Monitoring & Metrics
**Jira Stories:** TBD

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
REQUEST_COUNT = Counter('bluesky_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('bluesky_request_duration_seconds', 'Request duration')
ERROR_COUNT = Counter('bluesky_errors_total', 'Total errors', ['error_type'])

@REQUEST_DURATION.time()
@mcp.tool()
async def send_post(text: str) -> dict:
    REQUEST_COUNT.labels(method='POST', endpoint='send_post').inc()
    # ... implementation
```

## Implementation Timeline

### Single Developer Timeline
```
Phase 0 (Foundation): 1-2 days
├── Code organization and infrastructure setup
├── Critical for all subsequent development efficiency

Phase 1 (Safety): 1-2 weeks
├── Input validation & sanitization
├── Error handling & logging infrastructure
├── Essential before any production use

Phase 2 (Compliance): 1-2 weeks
├── Rate limiting implementation
├── API compliance & retry logic
├── Required to avoid Bluesky API bans

Phase 3 (Enhancement): 2-3 weeks
├── Advanced media handling & validation
├── Content processing improvements
├── Improves reliability and user experience

Phase 4 (Production): 1-2 weeks
├── Configuration management & CLI
├── Deployment infrastructure
├── Enables production deployment

Phase 5 (Optimization): 1 week
├── Performance optimization & monitoring
├── Polish and documentation
├── Optional - can be deferred if needed
```

### Single Developer Strategy

**Sequential Development Approach:**
- **Focus**: One phase at a time with deep, complete implementation
- **Advantage**: No coordination overhead, can make design decisions quickly
- **Approach**: Build each phase to completion before moving to next
- **Flexibility**: Can adjust priorities based on real-world testing feedback

**Development Workflow:**
- Complete Phase 0 foundation work first (critical for efficiency)
- Implement phases sequentially with thorough testing
- Regular self-review and documentation
- Incremental deployment and validation

## Development Readiness Assessment

### ✅ Ready for Development
- **Strategic Alignment**: Infrastructure-first approach properly sequenced
- **Foundation Phase**: Complete task breakdown for BS-000, BS-00A, BS-00B, BS-00C
- **Prototype Scope**: Appropriate complexity for development phase
- **Clear Dependencies**: Proper task sequencing and sprint structure

### 🟡 Gaps to Address During Development

#### Testing Strategy Considerations
- **Rate Limiting Testing**: Develop approach for testing rate limiting without hitting real Bluesky API limits
- **Integration Testing**: Define strategy for testing Bluesky API interactions (mocking vs. staging)
- **Unit Test Framework**: Set up testing infrastructure during Phase 0 (BS-000)
- **Test Data Management**: Create test accounts and sample data for development

#### Development Environment Setup
- **Local Development**: Document complete setup procedures for new developers
- **Mock/Staging Environment**: Consider setting up development Bluesky instance or comprehensive mocking
- **CI/CD Pipeline**: Define build, test, and deployment automation during Phase 0
- **Environment Configuration**: Document development vs. staging vs. production configurations

#### Documentation and Onboarding
- **API Documentation**: Set up automatic generation from code during development
- **Developer Onboarding**: Create step-by-step setup guide with troubleshooting
- **Configuration Examples**: Provide real-world configuration samples and explanations
- **Troubleshooting Guide**: Build comprehensive FAQ and common issues documentation

**Note**: These gaps are typical "discover as we go" items that don't block starting development. Address them incrementally during Sprint 1.

## Risk Mitigation

### Technical Risks

**Risk: Rate Limit Violations**
- **Mitigation**: Implement conservative limits with monitoring
- **Fallback**: Automatic backoff and queue management
- **Testing**: Load testing with actual Bluesky API

**Risk: Memory Leaks in Media Processing**
- **Mitigation**: Streaming processing for large files
- **Fallback**: File size limits and cleanup routines
- **Testing**: Memory profiling with large media files

**Risk: Configuration Drift**
- **Mitigation**: Version-controlled default configs
- **Fallback**: Validation on startup
- **Testing**: Config validation test suite

### Process Risks

**Risk: Burnout/Overcommitment**
- **Mitigation**: Realistic timeline estimates and phase boundaries
- **Fallback**: Defer Phase 5 (optimization) if needed
- **Testing**: Regular progress check-ins and scope validation

**Risk: Scope Creep**
- **Mitigation**: Strict phase definitions and acceptance criteria
- **Fallback**: Maintain MVP focus - defer advanced features
- **Testing**: Document all deferred features for future implementation

**Risk: Technical Debt Accumulation**
- **Mitigation**: Complete each phase thoroughly before moving on
- **Fallback**: Refactoring sprints between major phases
- **Testing**: Code quality reviews at each phase completion

### AI-Specific Risks

**Risk: AI-Generated Logic Errors**
- **Mitigation**: Never deploy AI code without thorough testing and review
- **Fallback**: Rollback to human-written implementation if AI bugs persist
- **Testing**: Comprehensive unit tests and integration tests for all AI-generated code

**Risk: Context Loss Across Sessions**
- **Mitigation**: Maintain detailed documentation and architectural decisions
- **Fallback**: Re-explain context to AI at start of each session
- **Testing**: Code review checklist to catch context-dependent errors

**Risk: Over-Reliance on AI for Complex Logic**
- **Mitigation**: Use AI for boilerplate/patterns only, human for business logic
- **Fallback**: Rewrite complex AI code manually if correction cycles become inefficient
- **Testing**: Flag complex functions for mandatory human review

## Quality Gates

### Phase Completion Criteria

**Phase 0 Complete When:**
- [ ] All tools moved to appropriate modules
- [ ] All existing tests pass
- [ ] Tool discovery works correctly
- [ ] Documentation updated

**Phase 1 Complete When:**
- [ ] All inputs validated with appropriate error messages
- [ ] No unhandled exceptions in any tool
- [ ] Structured logging implemented
- [ ] Error response format standardized

**Phase 2 Complete When:**
- [ ] Rate limiting never exceeded in load tests
- [ ] Exponential backoff working correctly
- [ ] Queue management handling bursts
- [ ] No API violations in extended testing

**Phase 3 Complete When:**
- [ ] All media formats handled correctly
- [ ] File size limits enforced
- [ ] Content processing working (hashtags, mentions)
- [ ] Media compression functioning

**Phase 4 Complete When:**
- [ ] YAML configuration loading
- [ ] CLI commands working
- [ ] Docker deployment successful
- [ ] Health checks responding

**Phase 5 Complete When:**
- [ ] Performance benchmarks met
- [ ] Monitoring dashboard functional
- [ ] Documentation complete
- [ ] Production deployment guide ready

## Success Metrics

### Technical Metrics
- **Zero rate limit violations** during testing
- **< 100ms response time** for 95% of requests
- **99.9% uptime** in development environment
- **100% test coverage** for critical paths

### Quality Metrics
- **Zero critical bugs** in production
- **< 1 day** mean time to resolution for issues
- **100% functionality** preserved through refactoring
- **< 5 minutes** deployment time

### Developer Experience Metrics
- **< 30 seconds** test suite execution time
- **< 5 minutes** full development environment setup
- **Clean git history** with meaningful commit messages
- **100% documentation coverage** for public APIs and design decisions

### Total Timeline Estimate
**Single Developer + AI Assistance**: 4-7 weeks total

**AI-Optimized Timeline:**
- **Phase 0**: 1 day (AI accelerated refactoring + 0.5 day correction)
- **Phase 1-2**: 1.5-3 weeks (AI validation patterns + human business logic + 20% correction buffer)
- **Phase 3**: 1-2 weeks (AI media utilities + human integration + correction cycles)
- **Phase 4**: 3-5 days (AI config/deploy templates + human testing)
- **Phase 5**: 2-3 days (AI optimization suggestions + human validation)

**Time Savings vs. Traditional:**
- **Boilerplate**: 60-80% faster (refactoring, configs, standard patterns)
- **Documentation**: 70% faster (AI generates, human reviews)
- **Testing**: 50% faster (AI generates cases, human validates logic)
- **Debugging**: 20% slower (AI bugs can be subtle and time-consuming)

## Conclusion

This development strategy prioritizes safety and compliance while enabling efficient parallel development. By addressing the highest-risk items first (validation, rate limiting) and organizing the codebase early, we minimize the chance of project-killing issues while building a maintainable, production-ready system.

The phased approach ensures that each stage builds upon a solid foundation, making future development faster and more reliable. Regular quality gates and success metrics provide clear checkpoints to ensure the project stays on track.

---

**Recommended AI-Assisted Development Approach:**

**Week 1: Foundation (AI-Accelerated)**
1. **Day 1**: Use AI for Phase 0 refactoring (MCP-94, MCP-95) - structural reorganization
2. **Day 2-3**: Human review, test, and correct AI refactoring work
3. **Day 4-5**: Start Phase 1 with AI-generated validation patterns + human business logic

**Week 2-3: Safety & Compliance (AI + Human)**
1. **AI Tasks**: Generate validation schemas, error handling patterns, test cases
2. **Human Tasks**: Business logic, edge case handling, integration testing
3. **Correction Cycles**: 1-2 iterations per major component
4. **Focus**: Input validation, rate limiting, comprehensive error handling

**Week 3-4: Production Features (Balanced)**
1. **AI Tasks**: Configuration templates, deployment scripts, standard media utilities
2. **Human Tasks**: Integration logic, debugging, performance validation
3. **Testing**: AI-generated test cases + human verification of business logic

**Week 5: Enhancement & Polish (AI-Supported)**
1. **AI Tasks**: Documentation generation, optimization suggestions, monitoring setup
2. **Human Tasks**: Final integration, performance tuning, production testing
3. **Buffer**: Extra time for final debugging and edge case fixes

### AI Workflow Per Task
1. **Plan**: Human defines requirements and acceptance criteria
2. **Generate**: AI creates initial implementation + tests + docs
3. **Review**: Human checks logic, edge cases, integration points
4. **Correct**: AI fixes identified issues (with human guidance)
5. **Validate**: Human tests and approves final implementation

### Critical AI Guidelines
- **Never blindly accept AI code** - always test and validate
- **Focus AI on patterns** - let humans handle business logic
- **Expect 20-30% correction overhead** - budget time for fixes
- **Document AI decisions** - explain why AI suggestions were accepted/rejected
- **Test incrementally** - validate AI output immediately

**Next Steps:**
1. Begin Phase 0 refactoring with AI assistance (MCP-94, MCP-95)
2. Set up AI development workflow and correction protocols
3. Create Phase 1 tasks with clear AI vs. human responsibilities
4. Establish rapid iteration cycles with immediate testing
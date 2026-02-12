# Arc42+C4 Documentation Templates

This directory contains templates for creating project documentation following the Arc42 architecture framework and C4 modeling approach.

## Template Organization

**Access Pattern**: `{first-tag}/{remaining-tags}.md`

```
templates-arc42-c4/
├── product/              # strategy, definition, reference, pdr
├── architecture/         # Arc42 sections + cross-cutting pages
│   ├── intro.md
│   ├── constraints.md
│   ├── context.md
│   ├── strategy.md
│   ├── building-blocks.md
│   ├── runtime.md
│   ├── deployment.md
│   ├── cross-cutting.md          (main page)
│   ├── cross-cutting-domain.md   (child)
│   ├── cross-cutting-security.md (child)
│   ├── cross-cutting-operations.md (child)
│   ├── cross-cutting-testing.md  (child)
│   ├── adr-summary.md
│   ├── quality.md
│   ├── risks.md
│   └── glossary.md
├── epic/                 # details, architecture, adr, pdr, file-plan, implementation-summary
└── release/              # record, notes, post-mortem
```

**Examples**:
- Product Strategy: `product/strategy.md`
- Epic Details: `epic/details.md`
- Epic ADR: `epic/adr.md`
- Release Notes: `release/notes.md`

## Usage

**Templates work across all backends** (Confluence, file-based, SharePoint, Notion).

### Template Structure

Each template includes:
- **Content sections**: Structured guidance based on Arc42/C4 methodology
- **Guidance comments**: Explaining what goes in each section
- **Examples**: Sample content where helpful

### Creating Documentation from Templates

1. **Choose template** using pattern: `{first-tag}/{remaining-tags}.md`
2. **Copy template** to your documentation backend
3. **Replace placeholders**:
   - `{epic-id}`: Actual epic ID (e.g., `SCOPE-42`)
   - `{version}`: Version number (e.g., `myproduct-2.5.0`)
   - `[Title]`: Actual title
   - `YYYY-MM-DD`: Actual date
4. **Fill sections** following guidance comments
5. **Apply tags** per documentation guide:
   - Confluence: Use metadata/labels
   - File-based: Add as first line (e.g., `tags: product, strategy`)
6. **Create child pages** when single topic exceeds 300 words

### Child Pages

**Architecture**:
- Cross-cutting main has 4 required children: domain, security, operations, testing

**Epic**:
- Epic details (parent) has 5 children: architecture, adr, pdr, file-plan, implementation-summary

**Release**:
- Release record (parent) has 2 children: notes, post-mortem

### Progressive Disclosure

Templates support the documentation philosophy:
- **Brief content** in main page
- **Child pages** for detailed topics (>300 words)
- **Cross-references** to related pages

## Template Customization

While these templates provide comprehensive structure, you can:
- **Add sections** specific to your project
- **Remove sections** that don't apply
- **Adjust depth** based on project complexity
- **Maintain tags** - they enable deterministic queries (tags are defined in the documentation guide and applied by your backend, not stored in templates)

## Template Maintenance

Templates are maintained in the `project-documentation` skill:
- **Location**: `~/.claude/skills/project-documentation/templates/`
- **Source of truth**: These templates
- **Updates**: When Arc42+C4 approach evolves

## BMAD Workflow Integration

This template system is aligned with BMAD Method v4 principles with **critical addition of System Architecture phase**:

⚠️ **CRITICAL**: BMAD v4's public documentation does not distinguish between system-level and epic-level architecture. This gap has been addressed.

**NEW Workflow Guides**:
- **WORKFLOW.md** - Complete BMAD-aligned workflow with phase progression (includes System Architecture)
- **COLLABORATIVE-WORKFLOW.md** - **Human-AI collaboration model**: How users are involved in creating PRDs, System Architecture, and Epics
- **PHASE-REFERENCE.md** - Quick reference for what documents to create in each phase
- **SYSTEM-ARCHITECTURE-PHASE.md** - Detailed guide for the missing system architecture layer

**Corrected Phase Sequence**:
1. **Phase 0**: Product Documentation (business view)
2. **Phase 0.5**: **System Architecture** ⚠️ (Arc42 12 chapters - technical system foundation) ← **WAS MISSING**
3. **Phase 1**: Epic Planning (define WHAT to build)
4. **Phase 2**: Epic Implementation (build feature within system architecture)
5. **Phase 3**: Epic Completion (document and update system architecture)

**Key BMAD Enhancements**:
- **System Architecture phase** (Arc42 12 chapters) - Foundation before epics
- Phase indicators in all templates (Planning, Architecture, Development, QA, Completion)
- Agent ownership clearly defined (Product Owner, Architect, Developer, QA Engineer, Technical Writer)
- Context dependencies documented (what requires what, including system architecture)
- Strategic alignment (epics link to product strategy AND system architecture)
- Context preservation between phases
- Living documentation (system architecture evolves as epics complete)

## Related Documentation

- **WORKFLOW.md**: Complete BMAD-aligned workflow (START HERE for overview)
- **COLLABORATIVE-WORKFLOW.md**: Human-AI collaboration model - user involvement at each phase (READ THIS to understand approval gates)
- **PHASE-REFERENCE.md**: Quick reference for phase transitions and document dependencies
- **SYSTEM-ARCHITECTURE-PHASE.md**: Detailed guide for system architecture phase
- **Documentation Guide**: `documentation-guide-arc42-c4.md` (defines WHAT to document)
- **Backend Implementation**: Backend-specific files (define HOW to store/retrieve)
- **Detailed Standard**: `design/scope-doc-arc42-c4.md` (comprehensive standard)

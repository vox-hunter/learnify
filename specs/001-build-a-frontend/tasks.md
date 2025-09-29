# Tasks: AI Loom React Frontend

**Input**: Design documents from `/specs/001-build-a-frontend/`- [x] T028 [P] File upload component in `frontend/src/components/forms/FileUpload.tsx`- [x] T029 [P] URL input component in `frontend/src/components/forms/URLInput.tsx`**Prer- [x] T033 [P] Quiz question component in `frontend/src/components/quiz/QuizQuestion.tsx`- [x] T034 [P] Multiple choice component in `frontend/src/components/quiz/MultipleChoice.tsx`- [x] T035 [P] Fill in blanks component in `frontend/src/components/quiz/FillInBlanks.tsx`- [x] T036 [P] True/False component in `frontend/src/components/quiz/TrueFalse.tsx`- [x] T037 [P] Short answer component in `frontend/src/components/quiz/ShortAnswer.tsx`ites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)

```text
1. Load plan.md from feature directory
   → ✅ Implementation plan found: React 18+ with Vite frontend
   → ✅ Extract: TypeScript, React, Vite, React Router, Axios, React Query
2. Load optional design documents:
   → ✅ data-model.md: 7 entities → TypeScript type definition tasks
   → ✅ contracts/: 5 API contracts → integration test tasks
   → ✅ research.md: Technology decisions → setup tasks
3. Generate tasks by category:
   → Setup: Vite project, TypeScript config, dependencies, linting
   → Tests: contract tests, component tests, E2E tests
   → Core: types, services, components, pages
   → Integration: routing, error handling, responsive design
   → Polish: performance, accessibility, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → ✅ All contracts have integration tests
   → ✅ All entities have TypeScript types
   → ✅ All pages have components and tests
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `frontend/tests/`
- **Backend preserved**: `backend/` (existing Python backend unchanged)

## Phase 3.1: Setup

- [x] T001 Create React + Vite project structure in `frontend/` directory per implementation plan
- [x] T002 Initialize TypeScript React project with Vite dependencies (React 18+, TypeScript 5.x)
- [x] T003 [P] Configure ESLint (Airbnb config), Prettier, and Husky pre-commit hooks in `frontend/`
- [x] T004 [P] Set up testing environment (Jest, React Testing Library, Playwright) in `frontend/`
- [x] T005 [P] Configure Vite build settings and environment variables in `frontend/vite.config.ts`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

### CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation

### Contract Tests [P]

- [x] T006 [P] Integration test for document upload API in `frontend/tests/integration/document-upload.test.ts`
- [x] T007 [P] Integration test for URL document API in `frontend/tests/integration/url-document.test.ts`
- [x] T008 [P] Integration test for course generation API in `frontend/tests/integration/course-generation.test.ts`
- [x] T009 [P] Integration test for course status API in `frontend/tests/integration/course-status.test.ts`
- [x] T010 [P] Integration test for authentication API in `frontend/tests/integration/authentication.test.ts`

### Component Tests [P]

- [x] T011 [P] Unit test for FileUpload component in `frontend/src/components/forms/FileUpload.test.tsx`
- [x] T012 [P] Unit test for URLInput component in `frontend/src/components/forms/URLInput.test.tsx`
- [x] T013 [P] Unit test for ProgressBar component in `frontend/src/components/ui/ProgressBar.test.tsx`
- [x] T014 [P] Unit test for QuizQuestion component in `frontend/src/components/quiz/QuizQuestion.test.tsx`
- [x] T015 [P] Unit test for FillInBlanks component in `frontend/src/components/quiz/FillInBlanks.test.tsx`

### E2E Tests [P]

- [x] T016 [P] Unit test for CourseList component in `frontend/src/components/pages/CourseList.test.tsx`
- [x] T017 [P] Unit test for QuizResults component in `frontend/src/components/pages/QuizResults.test.tsx`
- [x] T018 [P] Unit test for Dashboard component in `frontend/src/components/pages/Dashboard.test.tsx`

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### TypeScript Types [P]

- [x] T019 [P] Document entity types in `frontend/src/types/document.ts`
- [x] T020 [P] Course entity types in `frontend/src/types/course.ts`
- [x] T021 [P] Quiz entity types in `frontend/src/types/quiz.ts`
- [x] T022 [P] User entity types in `frontend/src/types/user.ts`
- [x] T023 [P] API response types in `frontend/src/types/api.ts`

### Services [P]

- [x] T024 [P] Document service API calls in `frontend/src/services/documentService.ts`
- [x] T025 [P] Course service API calls in `frontend/src/services/courseService.ts`
- [x] T026 [P] Authentication service API calls in `frontend/src/services/authService.ts`
- [x] T027 [P] HTTP client configuration with Axios in `frontend/src/services/httpClient.ts`

### Core Components [P]

- [x] T028 [P] FileUpload component in `frontend/src/components/forms/FileUpload.tsx`
- [x] T029 [P] URLInput component in `frontend/src/components/forms/URLInput.tsx`
- [x] T030 [P] Progress bar component in `frontend/src/components/ui/ProgressBar.tsx`
- [x] T031 [P] Button component in `frontend/src/components/ui/Button.tsx`
- [x] T032 [P] Input component in `frontend/src/components/ui/Input.tsx`

### Quiz Components [P]

- [x] T033 [P] QuizQuestion component in `frontend/src/components/quiz/QuizQuestion.tsx`
- [x] T034 [P] MultipleChoice component in `frontend/src/components/quiz/MultipleChoice.tsx`
- [x] T035 [P] FillInBlanks component in `frontend/src/components/quiz/FillInBlanks.tsx`
- [x] T036 [P] TrueFalse component in `frontend/src/components/quiz/TrueFalse.tsx`
- [x] T037 [P] ShortAnswer component in `frontend/src/components/quiz/ShortAnswer.tsx`

### Custom Hooks

- [x] T038 Custom hook for course generation status in `frontend/src/hooks/useCourseGeneration.ts`
- [x] T039 Custom hook for authentication state in `frontend/src/hooks/useAuth.ts`
- [x] T040 Custom hook for quiz progress in `frontend/src/hooks/useQuizProgress.ts`

## Phase 3.4: Pages and Navigation

### Page Components

- [ ] T041 HomePage component in `frontend/src/pages/HomePage/HomePage.tsx`
- [ ] T042 CoursePage component in `frontend/src/pages/CoursePage/CoursePage.tsx`
- [ ] T043 LoginPage component in `frontend/src/pages/LoginPage/LoginPage.tsx`
- [ ] T044 PrivacyPage component in `frontend/src/pages/LegalPages/PrivacyPage.tsx`
- [ ] T045 TermsPage component in `frontend/src/pages/LegalPages/TermsPage.tsx`

### Navigation and Routing

- [ ] T046 React Router setup and route configuration in `frontend/src/App.tsx`
- [ ] T047 Navigation component with responsive menu in `frontend/src/components/common/Navigation.tsx`
- [ ] T048 Layout component for consistent page structure in `frontend/src/components/layout/Layout.tsx`

## Phase 3.5: Integration

### State Management

- [ ] T049 React Context for authentication state in `frontend/src/contexts/AuthContext.tsx`
- [ ] T050 React Query setup and configuration in `frontend/src/providers/QueryProvider.tsx`
- [ ] T051 Global error boundary component in `frontend/src/components/common/ErrorBoundary.tsx`

### Styling and Responsiveness

- [ ] T052 CSS Modules setup and global styles in `frontend/src/styles/globals.module.css`
- [ ] T053 Responsive design implementation for breakpoints (768px, 1024px, 1440px)
- [ ] T054 Component-specific CSS modules for all components

### Utilities

- [ ] T055 Form validation utilities in `frontend/src/utils/validation.ts`
- [ ] T056 Date/time formatting utilities in `frontend/src/utils/formatters.ts`
- [ ] T057 Local storage utilities in `frontend/src/utils/storage.ts`

## Phase 3.6: Polish

### Performance Optimization [P]

- [ ] T058 [P] Implement lazy loading for heavy components using React.lazy()
- [ ] T059 [P] Bundle size analysis and optimization
- [ ] T060 [P] Image optimization and asset management
- [ ] T061 [P] Memoization for expensive computations using useMemo/useCallback

### Accessibility and Testing [P]

- [ ] T062 [P] Accessibility compliance implementation (WCAG 2.1 AA)
- [ ] T063 [P] Keyboard navigation support for all interactive elements
- [ ] T064 [P] Screen reader compatibility testing
- [ ] T065 [P] Component documentation with JSDoc comments

### Final Integration

- [ ] T066 End-to-end testing execution and validation
- [ ] T067 Performance testing with Lighthouse CI (≥90 scores required)
- [ ] T068 Cross-browser compatibility testing
- [ ] T069 Manual testing using quickstart.md scenarios
- [ ] T070 Production build optimization and deployment preparation

## Dependencies

**Setup Dependencies**:

- T001 → T002 → T003-T005 (sequential setup, then parallel config)

**Test Dependencies**:

- T003-T005 → T006-T018 (tests require setup completion)

**Implementation Dependencies**:

- T019-T023 (types) → T024-T027 (services) → T028-T037 (components)
- T038-T040 (hooks) depend on T019-T027 (types and services)
- T041-T045 (pages) depend on T028-T040 (components and hooks)
- T046-T048 (routing) depend on T041-T045 (pages)

**Integration Dependencies**:

- T049-T051 (state management) depend on T019-T027 (types and services)
- T052-T054 (styling) can run parallel with implementation
- T055-T057 (utilities) can run parallel with implementation

**Polish Dependencies**:

- T058-T061 (performance) depend on T028-T048 (components and pages)
- T062-T065 (accessibility) depend on T028-T048 (components and pages)
- T066-T070 (final testing) depend on ALL previous tasks

## Parallel Execution Examples

### Phase 3.2: Contract Tests (all parallel)

```typescript
// Launch T006-T010 together:
Task: "Integration test for document upload API in frontend/tests/integration/document-upload.test.ts"
Task: "Integration test for URL document API in frontend/tests/integration/url-document.test.ts"
Task: "Integration test for course generation API in frontend/tests/integration/course-generation.test.ts"
Task: "Integration test for course status API in frontend/tests/integration/course-status.test.ts"
Task: "Integration test for authentication API in frontend/tests/integration/authentication.test.ts"
```

### Phase 3.3: TypeScript Types (all parallel)

```typescript
// Launch T019-T023 together:
Task: "Document entity types in frontend/src/types/document.ts"
Task: "Course entity types in frontend/src/types/course.ts"
Task: "Quiz entity types in frontend/src/types/quiz.ts"
Task: "User entity types in frontend/src/types/user.ts"
Task: "API response types in frontend/src/types/api.ts"
```

### Phase 3.3: Core Components (all parallel after types complete)

```typescript
// Launch T028-T037 together:
Task: "FileUpload component in frontend/src/components/forms/FileUpload.tsx"
Task: "URLInput component in frontend/src/components/forms/URLInput.tsx"
Task: "ProgressBar component in frontend/src/components/common/ProgressBar.tsx"
Task: "QuizQuestion component in frontend/src/components/quiz/QuizQuestion.tsx"
Task: "FillInBlanks component in frontend/src/components/quiz/FillInBlanks.tsx"
// ... and so on
```

## Notes

- [P] tasks = different files, no dependencies between them
- Verify all tests fail before implementing components
- Commit after each completed task
- Follow constitutional requirements: TypeScript strict mode, ESLint Airbnb config
- Maintain <500KB gzipped bundle size throughout development
- Preserve all existing backend API contracts

## Task Generation Rules Applied

1. **Contract files**: 5 contracts → 5 integration test tasks (T006-T010) [P]
2. **Data model entities**: 7 entities → 5 TypeScript type files (T019-T023) [P]
3. **User stories**: 7 quickstart scenarios → 3 E2E test tasks (T016-T018) [P]
4. **Components**: Based on pages and functionality → 20+ component tasks [P]
5. **Dependencies**: Tests before implementation, types before services, services before components

## Validation Checklist

- ✅ All contracts have integration tests (T006-T010)
- ✅ All entities have TypeScript types (T019-T023)
- ✅ All pages have components and tests (T041-T045 with T011-T018)
- ✅ TDD approach: tests written before implementation
- ✅ Parallel tasks marked correctly for independent files
- ✅ Dependencies clearly documented
- ✅ Constitutional requirements addressed (TypeScript, testing, performance)
- ✅ Existing backend API contracts preserved

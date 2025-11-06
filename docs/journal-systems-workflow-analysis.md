# Journal Management Systems: Workflow & Dashboard Design Analysis

**Research Date**: January 2025
**Purpose**: Understand how mature journal management systems (OJS, ScholarOne, Editorial Manager) have designed their workflows and dashboards over years of development.

---

## Executive Summary

After researching OJS 3.5 (2025), ScholarOne Manuscripts, and Editorial Manager (Aries Systems), several key patterns emerge that define successful journal management systems:

1. **4-Stage Workflow Model** is the industry standard
2. **Task-Centric Dashboards** with filtered queues
3. **Inline Discussions** at every stage (critical!)
4. **Participant Management** with flexible role assignment
5. **File Versioning** throughout the workflow
6. **Status Tracking** with visual indicators
7. **Minimal Clicks** - every redesign focuses on reducing friction
8. **Side Panel Workflows** for quick actions without page changes

---

## Part 1: The 4-Stage Workflow Model

### Universal Pattern Across All Systems

Every mature journal management system converged on a **4-stage editorial workflow**:

```
Submission → Review → Copyediting → Production
```

**Why This Works:**
- Maps to real-world editorial process
- Clear separation of concerns
- Each stage has distinct roles and responsibilities
- Natural progression with decision points

### Stage Details from OJS 3.4/3.5

#### **Stage 1: Submission**
- **Purpose**: Initial triage and assignment
- **Key Actions**:
  - Desk reject inappropriate submissions
  - Assign to Section Editor
  - Initial quality check
  - Send to Review or reject
- **Decision Point**: "Is this worth reviewing?"

#### **Stage 2: Review**
- **Purpose**: Peer review and author revisions
- **Key Actions**:
  - Assign reviewers
  - Manage review rounds (can have multiple)
  - Request author revisions
  - Make acceptance/rejection decision
- **Decision Point**: "Does this meet publication standards?"
- **OJS 3.4 Feature**: Can cancel a review round (unless reviews completed)

#### **Stage 3: Copyediting**
- **Purpose**: Language and style improvement
- **Key Actions**:
  - Assign copyeditor
  - Copyeditor downloads and edits files
  - Upload copyedited version
  - **Author Review Step** (critical!)
  - Editor approval
- **Decision Point**: "Are copyedits approved?"

#### **Stage 4: Production**
- **Purpose**: Convert to publication formats
- **Key Actions**:
  - Layout editing
  - Proofreading
  - Galley generation (PDF, HTML, XML, EPUB)
  - Final approval
  - Schedule for publication
- **Decision Point**: "Ready to publish?"

---

## Part 2: Dashboard Design Patterns

### OJS 3.5 Dashboard Redesign (June 2025)

**Major Innovation**: Completely redesigned editorial dashboard with focus on **reducing friction**.

#### Key Improvements:

1. **Filtered Views for Quick Access**
   - Active submissions
   - My assigned submissions
   - By stage (Submission/Review/Copyediting/Production)
   - By status
   - Archived

2. **Inline Side Panel Workflow**
   ```
   Dashboard List → Click submission → Side panel slides in
                                      → View details
                                      → Take action
                                      → Panel closes
                                      → Next item automatically
   ```
   - **Result**: Fewer clicks, faster task completion
   - No full page reloads for simple actions

3. **Status Icons & Action Buttons**
   - Visual indicators for submission state
   - Clear next-action buttons
   - Overdue warnings
   - Color-coded priorities

4. **Task Queue Pattern**
   - "Needs action:" section at top
   - Shows count of pending tasks
   - Click task type → filtered queue appears
   - Complete task → auto-advance to next

5. **Left Sidebar Navigation**
   - All workflow stages accessible via sidebar
   - Current stage highlighted
   - Quick jump between stages
   - Persistent across all views

#### Design Philosophy (from OJS 3.5 UX Lead):

> "The redesign was rooted in **scalability and inclusivity**—creating a space where people regardless of background, experience, or role could easily understand information and feel empowered to take action without barriers."

**Key Principles:**
- **Clarity**: Information architecture is obvious
- **Simplicity**: Remove unnecessary complexity
- **Flexibility**: Customizable views per user
- **No one left behind**: Works for beginners and experts

---

## Part 3: The Participants Panel Pattern

### Universal Feature Across All Systems

Every mature system has a **Participants** panel showing:

```
┌─────────────────────────────┐
│     PARTICIPANTS            │
├─────────────────────────────┤
│ 👤 John Doe (Editor)        │▼│
│ 👤 Jane Smith (Author)      │▼│
│ 👤 Bob Wilson (Reviewer)    │▼│
│                             │
│ [+ Add Participant]         │
└─────────────────────────────┘
```

**Features:**
- Shows all people involved in this submission
- Their role clearly labeled
- Click dropdown (▼) to:
  - Send message (start discussion)
  - Remove from submission
  - Change role/permissions
- **Add Participant** button to bring in new people at any stage

**Why This Matters:**
- Transparency: Everyone knows who's involved
- Quick communication: One click to message anyone
- Flexible: Can add/remove people as needs change
- Audit trail: Shows who participated when

---

## Part 4: Discussion/Messaging System

### The Game-Changer Feature

**OJS 3.x Innovation**: Internal discussion feature **at each stage**.

#### How It Works:

```
COPYEDITING DISCUSSIONS
┌───────────────────────────────────────────┐
│ 📝 Copyedits Complete - Please Review    │
│    From: Sarah (Copyeditor)               │
│    To: John (Editor), Mary (Author)       │
│    📎 manuscript-copyedited.docx          │
│    [View Thread]                          │
├───────────────────────────────────────────┤
│ 📝 Question about Figure 3                │
│    From: Sarah (Copyeditor)               │
│    To: Mary (Author)                      │
│    [View Thread]                          │
└───────────────────────────────────────────┘
[+ Add Discussion]
```

**Key Features:**
1. **Stage-Specific**: Discussions tied to workflow stage
2. **Threaded**: Full conversation history preserved
3. **File Attachments**: Can attach files to discussions
4. **Email Notifications**: Recipients get email alerts
5. **Permanent Record**: Becomes part of editorial history
6. **Multiple Concurrent Discussions**: Can have several threads per stage

**Why This Is Critical:**
- **Replaces scattered emails**: Everything in one place
- **Context preservation**: Discussion stays with submission
- **Accountability**: Clear record of who said what when
- **Flexible communication**: Can loop in anyone

**Implementation Pattern:**
```javascript
// Simplified structure
Discussion {
  id: number
  stage: "copyediting" | "review" | "production"
  participants: User[]
  subject: string
  messages: Message[]
  attachments: File[]
  created_at: datetime
  status: "active" | "closed"
}
```

---

## Part 5: File Management Patterns

### File Versioning Throughout Workflow

Every system maintains **multiple file versions**:

```
SUBMISSION FILES
└─ Original Submission
   └─ manuscript-v1.docx

REVIEW FILES
└─ Revised Manuscript (Round 1)
   └─ manuscript-v2-revised.docx
└─ Revised Manuscript (Round 2)
   └─ manuscript-v3-final-revised.docx

COPYEDITING FILES
├─ Draft Files
│  └─ manuscript-v3-final-revised.docx (from review)
└─ Copyedited Files
   └─ manuscript-copyedited.docx

PRODUCTION FILES
├─ Production Ready Files
│  └─ manuscript-copyedited-approved.docx
└─ Galleys
   ├─ manuscript-final.pdf
   ├─ manuscript-final.html
   └─ manuscript-final.xml
```

**Upload Process** (3-Step Pattern from OJS):

1. **Upload File**
   - Drag & drop or file picker
   - File type validation
   - Progress indicator

2. **Review Details**
   - Confirm/edit filename
   - Add description
   - Set file metadata
   - Choose file type/category

3. **Confirm**
   - Final review
   - Submit
   - Attach to discussion (optional)

**File Organization Principles:**
- **Separate panels** for each file category
- **Clear labeling** of what each file is
- **Download buttons** prominent
- **Version history** tracked
- **File type icons** for visual recognition

---

## Part 6: Editorial Decision Workflow

### Decision Points at Each Stage

Systems handle editorial decisions consistently:

#### Decision UI Pattern:

```
┌──────────────────────────────────────┐
│  EDITORIAL DECISION                   │
├──────────────────────────────────────┤
│  Decision: [▼ Select Decision]       │
│                                       │
│  Options:                             │
│  • Accept Submission                  │
│  • Revisions Required                 │
│  • Resubmit for Review                │
│  • Decline Submission                 │
│  • Send to Copyediting     ← (common) │
│  • Send to Production      ← (common) │
│                                       │
│  Notify Author: [✓]                   │
│                                       │
│  Email Template: [▼ Select Template] │
│                                       │
│  Message to Author:                   │
│  ┌──────────────────────────────────┐│
│  │ [Customizable message]           ││
│  └──────────────────────────────────┘│
│                                       │
│  [Record Decision]                    │
└──────────────────────────────────────┘
```

**Features:**
- **Pre-defined decision types** (not free-form)
- **Email templates** for each decision
- **Customizable message** while using template
- **Automatic notifications** to relevant parties
- **History tracking** of all decisions

---

## Part 7: ScholarOne & Editorial Manager Patterns

### ScholarOne Manuscripts

**Key Differentiators:**

1. **Real-Time Dashboard**
   - "Intuitive dashboard for authors, reviewers, and editors"
   - Real-time submission status updates
   - Live progress indicators

2. **Reporting & Analytics**
   - Track review times
   - Acceptance rates
   - Reviewer performance
   - Bottleneck identification

3. **Best Practice Workflows**
   - Pre-review screening checklists
   - Automatic assignment algorithms
   - Concurrent reviews (parallel processing)
   - Online annotation tools

4. **Integration Focus**
   - ORCID single sign-on
   - CRediT taxonomy for contributor roles
   - Publons for peer review tracking
   - Citation databases

### Editorial Manager (Aries Systems)

**2024-2025 Redesign Focus:**

1. **Role-Based Phased Redesign**
   - Phase 1: Editor role (2024)
   - Phase 2: Reviewer role
   - Phase 3: Author role
   - Phase 4: Publisher role

2. **Modern Main Navigation Bar**
   - Responsive design
   - Clearer information hierarchy
   - Reduced clicks

3. **Roadmap Priorities (2024+)**
   - UI/UX enhancements
   - Improved author experience
   - Single user identity across all journals
   - In-system messaging
   - Support tooltips
   - Enhanced data reporting

4. **Editor Decision Form**
   - New digital prototype shown at 2024 conference
   - Focus on streamlined decision-making
   - Visual feedback on decision impact

---

## Part 8: Task Management Patterns

### "Needs Action" Queue Design

**Pattern from OJS 3.5**:

```
NEEDS ACTION (23)
┌─────────────────────────────────────────┐
│ 📋 Awaiting Desk Review (5)            │→│
│ 📋 Reviewers Need Assignment (8)       │→│
│ 📋 Reviews Complete - Decision Needed (3)│→│
│ 📋 Awaiting Author Revisions (4)       │→│
│ 📋 Copyediting Complete - Review (2)   │→│
│ 📋 Production Files Ready (1)          │→│
└─────────────────────────────────────────┘

Click any → Opens filtered queue
Complete task → Auto-advance to next
Counter updates in real-time
```

**Psychology of Good Task Queues:**

1. **Visible Progress**: See tasks completed
2. **Small Chunks**: Break work into manageable pieces
3. **Auto-Advance**: Flow from task to task
4. **Count Down**: Motivating to see numbers decrease
5. **Clear Priority**: What needs attention now

### Task Card Pattern

When viewing a queue:

```
┌──────────────────────────────────────────┐
│ MS-2025-042: "Machine Learning in Med"  │
│                                          │
│ Author: John Smith                       │
│ Submitted: Jan 15, 2025 (3 days ago)    │
│ Status: ⚠️ DESK REVIEW - Overdue        │
│                                          │
│ [Quick Reject] [Assign Editor] [Details]│
└──────────────────────────────────────────┘
```

**Key Elements:**
- Manuscript ID and title
- Key metadata (author, date)
- Status with visual indicator
- Quick action buttons
- Link to full details

---

## Part 9: Copyediting Workflow Deep Dive

### OJS Copyediting Stage - Step-by-Step

**1. Transition to Copyediting**
```
Review Stage → [Send to Copyediting] button
             → Copyeditor automatically added to Participants
             → Discussion created with notification
```

**2. Copyeditor Receives Assignment**
- Email notification received
- Logs into dashboard
- Sees submission in "My Assigned" queue
- Clicks [Copyediting] link

**3. Copyeditor Downloads Files**
```
DRAFT FILES Panel
┌─────────────────────────────────────┐
│ 📄 manuscript-reviewed.docx         │
│    Version 2.0 | 250 KB              │
│    [Download]                        │
└─────────────────────────────────────┘
```
- Downloads to local computer
- Edits using Word/Google Docs/etc
- Works outside the system

**4. Copyeditor Uploads Completed Work**
```
[+ Add Discussion]
→ Recipients: [✓] Section Editor [✓] Author
→ Subject: "Copyediting Complete"
→ Message: "I've completed copyediting..."
→ Attach File: [Upload] manuscript-copyedited.docx
   └─ 3-step upload process
→ [Send]
```

**5. Author Review Process** (Critical!)
- Author receives notification
- Downloads copyedited version
- Reviews changes
- Responds via discussion:
  - Option A: "Approved - looks good"
  - Option B: "Please revise - see comments"

**6. Editor Approval**
- Reviews copyedited file
- Checks author approval
- Makes final decision:
  - If approved: [Send to Production]
  - If changes needed: Request updates

### Key Insight: Asynchronous Collaboration

**The copyediting pattern is fundamentally asynchronous:**
- Copyeditor works offline
- Uploads when complete
- Author reviews at their convenience
- Editor approves when ready

**This requires:**
- Clear notification system
- Obvious "next action" indicators
- File version tracking
- Discussion threads for questions

---

## Part 10: Production Workflow Patterns

### Galley Generation - The Final Step

**Production Stage Tasks:**

1. **Layout Editing**
   - Format for publication
   - Apply journal style
   - Add headers/footers
   - Page numbering

2. **Proofreading**
   - Final error check
   - Formatting verification
   - Consistency check

3. **Galley Creation**
   - Generate PDF (primary)
   - Generate HTML (web viewing)
   - Generate XML/JATS (indexing)
   - Optional: EPUB (e-readers)

### Galley Management UI Pattern

```
GALLEY FILES
┌──────────────────────────────────────────┐
│ 📕 PDF   | Article-Final.pdf  | 2.1 MB  │
│          [View] [Download] [Replace]     │
├──────────────────────────────────────────┤
│ 🌐 HTML  | Article-Final.html | 450 KB  │
│          [View] [Download] [Replace]     │
├──────────────────────────────────────────┤
│ 📊 XML   | Article-Final.xml  | 180 KB  │
│          [View] [Download] [Replace]     │
└──────────────────────────────────────────┘
[+ Generate New Galley]
```

**Features:**
- Multiple format support
- Preview capability
- Replace/update files
- Clear file size/format labels
- Generation tools for automation

---

## Part 11: Dashboard Component Hierarchy

### Information Architecture

**Primary Dashboard View:**

```
┌─────────────────────────────────────────────────────────┐
│  JOURNAL NAME                    [Profile] [Notifications]│
├─────────────────────────────────────────────────────────┤
│                                                          │
│  NEEDS ACTION (15)                                      │
│  ┌────────────────────────────────┐                    │
│  │ Task queues here...            │                    │
│  └────────────────────────────────┘                    │
│                                                          │
│  ACTIVE SUBMISSIONS                                      │
│  ┌────────────────────────────────┐                    │
│  │ Search: [________] 🔍          │                    │
│  │                                │                    │
│  │ Filters:                       │                    │
│  │ [All Stages ▼] [All Status ▼] │                    │
│  │                                │                    │
│  │ Submission List Table          │                    │
│  │ ┌──────────────────────────┐  │                    │
│  │ │ Rows of submissions...   │  │                    │
│  │ └──────────────────────────┘  │                    │
│  │                                │                    │
│  │ < Prev | Page 1 of 5 | Next > │                    │
│  └────────────────────────────────┘                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Submission Detail View (Side Panel or Full Page):**

```
┌─── SUBMISSION DETAILS ─────────────────────────────────┐
│                                                         │
│  MS-2025-042: Machine Learning in Medical Diagnosis    │
│  Current Stage: COPYEDITING                            │
│                                                         │
│  ├─ Submission                                         │
│  ├─ Review                                             │
│  ├─ Copyediting        ← (Active)                      │
│  └─ Production                                         │
│                                                         │
├──────────────────────────────────────────────────────┤
│  PARTICIPANTS                                          │
│  ┌──────────────────────────────────────────────────┐│
│  │ 👤 John Smith (Author)                 [▼]      ││
│  │ 👤 Jane Editor (Editor)                [▼]      ││
│  │ 👤 Bob Copyeditor (Copyeditor)         [▼]      ││
│  └──────────────────────────────────────────────────┘│
│  [+ Add Participant]                                  │
│                                                         │
├──────────────────────────────────────────────────────┤
│  COPYEDITING DISCUSSIONS (2)                           │
│  ┌──────────────────────────────────────────────────┐│
│  │ 📝 Copyediting Complete                          ││
│  │    From: Bob Copyeditor                          ││
│  │    2 hours ago | 3 messages                      ││
│  │    [View Thread]                                 ││
│  └──────────────────────────────────────────────────┘│
│  [+ Add Discussion]                                   │
│                                                         │
├──────────────────────────────────────────────────────┤
│  FILES                                                 │
│  Draft Files (1)                                       │
│  ┌──────────────────────────────────────────────────┐│
│  │ 📄 manuscript-reviewed.docx                      ││
│  │    [Download]                                    ││
│  └──────────────────────────────────────────────────┘│
│                                                         │
│  Copyedited Files (1)                                  │
│  ┌──────────────────────────────────────────────────┐│
│  │ 📄 manuscript-copyedited.docx                    ││
│  │    [Download]                                    ││
│  └──────────────────────────────────────────────────┘│
│  [Upload File]                                        │
│                                                         │
├──────────────────────────────────────────────────────┤
│  EDITORIAL ACTIONS                                     │
│  [Send to Production] [Request Changes] [View History]│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Part 12: Best Practices Synthesis

### What Makes a Dashboard Great?

Based on OJS 3.5, ScholarOne, and Editorial Manager redesigns:

#### 1. **Reduce Friction**
- Every redesign focuses on fewer clicks
- Inline actions where possible
- Side panels for quick views
- Auto-advance through tasks

#### 2. **Clear Visual Hierarchy**
- What needs attention is obvious
- Status indicators are prominent
- Action buttons stand out
- Important info at the top

#### 3. **Progressive Disclosure**
- Show summary, hide details
- Expand on demand
- Don't overwhelm with information
- Context-sensitive help

#### 4. **Consistent Patterns**
- Same UI for similar actions across stages
- Predictable locations for common elements
- Familiar metaphors (folders, discussions, etc.)

#### 5. **Smart Defaults**
- Pre-fill forms when possible
- Remember user preferences
- Suggest appropriate actions
- Auto-assign when logical

#### 6. **Immediate Feedback**
- Loading indicators
- Success/error messages
- Live updates
- Progress indicators

#### 7. **Accessible to All**
- Works for beginners and experts
- Multiple ways to accomplish tasks
- Good keyboard navigation
- Screen reader friendly

### What Makes a Workflow Successful?

#### 1. **Maps to Real World**
- Mirrors actual editorial process
- Familiar terminology
- Natural progression
- Logical decision points

#### 2. **Flexible but Structured**
- Can skip steps when appropriate
- Can go back if needed
- Can add participants anytime
- But default path is clear

#### 3. **Asynchronous Collaboration**
- People work at their own pace
- No one is blocked
- Notifications keep things moving
- Clear handoffs between roles

#### 4. **Complete Communication**
- All discussions preserved
- Email notifications for external alerts
- In-system for context
- File sharing integrated

#### 5. **Audit Trail**
- Every action logged
- Decision history visible
- File versions tracked
- Participant changes recorded

---

## Part 13: Common Pitfalls to Avoid

### Lessons from Mature Systems

#### 1. **Over-Complication**
- ❌ Too many fields in forms
- ❌ Too many steps to complete action
- ❌ Too many options to choose from
- ✅ Keep forms minimal, progressive disclosure

#### 2. **Poor Navigation**
- ❌ Hard to find submissions
- ❌ Get lost in nested menus
- ❌ Can't tell where you are
- ✅ Breadcrumbs, clear hierarchy, always show context

#### 3. **Weak Notifications**
- ❌ Miss important updates
- ❌ Too many notifications (noise)
- ❌ Unclear what action is needed
- ✅ Smart notifications, digest options, clear CTAs

#### 4. **File Management Chaos**
- ❌ Can't find the right version
- ❌ Unclear which file to download
- ❌ Lost files
- ✅ Clear labeling, version history, organized panels

#### 5. **Ignoring Mobile**
- ❌ Desktop-only design
- ❌ Tiny buttons on mobile
- ❌ Horizontal scrolling
- ✅ Responsive design, mobile-first actions

---

## Part 14: Feature Comparison Matrix

| Feature | OJS 3.5 | ScholarOne | Editorial Manager | Our System |
|---------|---------|------------|-------------------|------------|
| **4-Stage Workflow** | ✅ | ✅ | ✅ | ✅ |
| **Inline Side Panel** | ✅ | ❓ | ✅ (New) | ⏳ TODO |
| **Stage Discussions** | ✅ | ✅ | ✅ | ✅ Backend |
| **Participants Panel** | ✅ | ✅ | ✅ | ⏳ TODO |
| **Task Queue** | ✅ | ✅ | ✅ | ⏳ TODO |
| **File Versioning** | ✅ | ✅ | ✅ | ✅ Backend |
| **ORCID Integration** | ✅ | ✅ | ✅ | ✅ |
| **Real-time Updates** | ✅ | ✅ | ✅ | ⏳ TODO |
| **Mobile Responsive** | ✅ | ✅ | ✅ | ⏳ TODO |
| **Automated Galleys** | ❌ | ❌ | ❌ | ✅ (Advantage!) |
| **AI-Powered Matching** | ❌ | ✅ (paid) | ✅ (paid) | ✅ (Advantage!) |
| **Modern React UI** | ❌ (PHP) | ❌ | ❌ | ✅ (Advantage!) |
| **Free & Open Source** | ✅ | ❌ | ❌ | ✅ (Advantage!) |

---

## Part 15: Implementation Recommendations

### Priority Features to Add

Based on this research, here's what we should prioritize:

#### **P0 (Critical - Next Week)**

1. **Inline Side Panel Pattern**
   - Click submission in list → side panel slides in
   - Quick actions without page reload
   - Auto-advance to next item

2. **Participants Panel**
   - Show all involved users
   - Quick message/discussion starting
   - Add/remove participants
   - Visual role indicators

3. **Task Queue Dashboard**
   - "Needs Action" section at top
   - Grouped by action type
   - Show counts
   - One-click to filtered queue

4. **Discussion UI**
   - Thread view for each discussion
   - File attachments visible
   - Reply inline
   - Email notification toggle

#### **P1 (Important - Next Two Weeks)**

5. **Filtered Views**
   - By stage
   - By status
   - By assigned user
   - By date range

6. **File Management UI**
   - Separate panels by category
   - Clear version labeling
   - Download/upload in context
   - Preview capability

7. **Editorial Decision Form**
   - Pre-defined decisions
   - Email template integration
   - Customizable message
   - Notify checkboxes

8. **Status Indicators**
   - Visual status badges
   - Color coding
   - Overdue warnings
   - Progress indicators

#### **P2 (Enhancement - Future)**

9. **Real-time Updates**
   - WebSocket for live updates
   - No page refresh needed
   - Collaborative editing indicators

10. **Advanced Analytics**
    - Time-in-stage metrics
    - Bottleneck identification
    - Reviewer performance
    - Acceptance rates

11. **Mobile Optimization**
    - Touch-friendly buttons
    - Simplified mobile views
    - Swipe gestures

12. **Accessibility**
    - WCAG 2.1 AA compliance
    - Keyboard navigation
    - Screen reader optimization

---

## Part 16: UI Component Library Needs

### Components We Need to Build

Based on mature systems, here are the core components:

#### **Dashboard Components**

1. **TaskQueue**
   ```tsx
   <TaskQueue
     title="Needs Action"
     tasks={[
       { type: 'desk_review', count: 5, urgent: true },
       { type: 'assign_reviewers', count: 8, urgent: false }
     ]}
     onTaskClick={handleTaskClick}
   />
   ```

2. **SubmissionList**
   ```tsx
   <SubmissionList
     submissions={submissions}
     columns={['id', 'title', 'author', 'stage', 'status', 'date']}
     filters={filters}
     onRowClick={handleRowClick}
     selectable
   />
   ```

3. **SidePanel**
   ```tsx
   <SidePanel
     isOpen={showPanel}
     onClose={handleClose}
     width="wide" // or "narrow"
   >
     <SubmissionDetail id={selectedId} />
   </SidePanel>
   ```

#### **Workflow Components**

4. **ParticipantsPanel**
   ```tsx
   <ParticipantsPanel
     participants={[
       { id: 1, name: 'John', role: 'editor', canRemove: true },
       { id: 2, name: 'Jane', role: 'author', canRemove: false }
     ]}
     onAddParticipant={handleAdd}
     onRemoveParticipant={handleRemove}
     onMessageParticipant={handleMessage}
   />
   ```

5. **DiscussionThread**
   ```tsx
   <DiscussionThread
     discussion={discussion}
     onReply={handleReply}
     onAttachFile={handleAttach}
     allowedParticipants={participants}
   />
   ```

6. **FilePanel**
   ```tsx
   <FilePanel
     title="Draft Files"
     files={files}
     allowUpload
     allowDelete
     showPreview
     onDownload={handleDownload}
     onUpload={handleUpload}
   />
   ```

7. **WorkflowStepper**
   ```tsx
   <WorkflowStepper
     stages={['Submission', 'Review', 'Copyediting', 'Production']}
     currentStage="copyediting"
     onStageClick={handleStageClick}
   />
   ```

8. **DecisionForm**
   ```tsx
   <DecisionForm
     availableDecisions={decisions}
     emailTemplates={templates}
     onSubmit={handleDecision}
     notifyParticipants={['author', 'editor']}
   />
   ```

#### **Status Components**

9. **StatusBadge**
   ```tsx
   <StatusBadge
     status="in_progress"
     showIcon
     size="md"
   />
   ```

10. **OverdueIndicator**
    ```tsx
    <OverdueIndicator
      dueDate={dueDate}
      status={status}
      showDaysOverdue
    />
    ```

---

## Part 17: Database Schema Enhancements Needed

### Additional Tables to Consider

Based on mature systems:

```sql
-- Discussions (we need this!)
CREATE TABLE discussions (
  id SERIAL PRIMARY KEY,
  manuscript_id INT REFERENCES manuscripts(id),
  stage VARCHAR(50) NOT NULL, -- submission, review, copyediting, production
  subject VARCHAR(500) NOT NULL,
  created_by_id INT REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'active' -- active, closed
);

-- Discussion Messages
CREATE TABLE discussion_messages (
  id SERIAL PRIMARY KEY,
  discussion_id INT REFERENCES discussions(id),
  user_id INT REFERENCES users(id),
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Discussion Participants
CREATE TABLE discussion_participants (
  discussion_id INT REFERENCES discussions(id),
  user_id INT REFERENCES users(id),
  PRIMARY KEY (discussion_id, user_id)
);

-- Discussion Attachments
CREATE TABLE discussion_attachments (
  id SERIAL PRIMARY KEY,
  discussion_id INT REFERENCES discussions(id),
  message_id INT REFERENCES discussion_messages(id),
  file_id INT REFERENCES manuscript_files(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Manuscript Participants (broader than just authors)
CREATE TABLE manuscript_participants (
  manuscript_id INT REFERENCES manuscripts(id),
  user_id INT REFERENCES users(id),
  role VARCHAR(50) NOT NULL, -- editor, reviewer, copyeditor, author, etc.
  stage VARCHAR(50), -- which stage they're involved in
  added_at TIMESTAMP DEFAULT NOW(),
  added_by_id INT REFERENCES users(id),
  PRIMARY KEY (manuscript_id, user_id, role, stage)
);

-- Editorial Decisions (comprehensive history)
CREATE TABLE editorial_decisions (
  id SERIAL PRIMARY KEY,
  manuscript_id INT REFERENCES manuscripts(id),
  stage VARCHAR(50) NOT NULL,
  decision_type VARCHAR(100) NOT NULL,
  decision_label VARCHAR(200),
  editor_id INT REFERENCES users(id),
  message_to_author TEXT,
  email_template_used VARCHAR(200),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Workflow History (audit trail)
CREATE TABLE workflow_history (
  id SERIAL PRIMARY KEY,
  manuscript_id INT REFERENCES manuscripts(id),
  from_stage VARCHAR(50),
  to_stage VARCHAR(50),
  from_status VARCHAR(50),
  to_status VARCHAR(50),
  changed_by_id INT REFERENCES users(id),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Part 18: API Enhancements Needed

### Additional Endpoints Based on Research

```python
# Discussions API
POST   /api/v1/discussions/                    # Create discussion
GET    /api/v1/discussions/{id}                # Get discussion with messages
POST   /api/v1/discussions/{id}/messages       # Add message to discussion
POST   /api/v1/discussions/{id}/participants   # Add participant
DELETE /api/v1/discussions/{id}/participants/{user_id}  # Remove participant
POST   /api/v1/discussions/{id}/close          # Close discussion
GET    /api/v1/manuscripts/{id}/discussions    # Get all discussions for manuscript

# Participants API
GET    /api/v1/manuscripts/{id}/participants   # Get all participants
POST   /api/v1/manuscripts/{id}/participants   # Add participant
DELETE /api/v1/manuscripts/{id}/participants/{user_id}/{role}  # Remove
PATCH  /api/v1/manuscripts/{id}/participants/{user_id}  # Update role

# Editorial Decisions API
GET    /api/v1/manuscripts/{id}/decisions      # Decision history
POST   /api/v1/manuscripts/{id}/decisions      # Record new decision
GET    /api/v1/decisions/templates             # Get email templates

# Workflow History API
GET    /api/v1/manuscripts/{id}/history        # Complete audit trail
GET    /api/v1/manuscripts/{id}/timeline       # Visual timeline

# Task Queue API
GET    /api/v1/tasks/my-queue                  # User's task queue
GET    /api/v1/tasks/counts                    # Task counts by type
GET    /api/v1/tasks/overdue                   # Overdue items
```

---

## Conclusion: Key Takeaways

### What Mature Systems Teach Us

1. **The 4-stage workflow is not arbitrary** - It emerged from decades of real-world editorial practice

2. **Discussions are critical** - Every system added internal messaging after launching because scattered emails don't scale

3. **Reducing clicks obsessively** - Every major redesign focuses on fewer clicks, inline actions, side panels

4. **Participants must be visible** - Transparency about who's involved at each stage is fundamental

5. **File versioning matters** - Tracking versions throughout workflow prevents confusion and lost work

6. **Task queues are motivating** - "Needs Action" with counts helps editors prioritize and see progress

7. **Status indicators are powerful** - Visual cues (colors, icons, badges) communicate state instantly

8. **Mobile is table stakes** - In 2025, systems must work on phones and tablets

9. **Accessibility is not optional** - Academic publishing must be inclusive

10. **Simplicity wins** - The best systems feel obvious to use, regardless of user's technical skill

### Our Competitive Advantages

We can leapfrog established systems in several ways:

1. **Modern Tech Stack** - React, TypeScript, FastAPI vs. legacy PHP
2. **AI Integration** - Built-in reviewer matching, automated quality checks
3. **Automated Galleys** - One-click generation of multiple formats
4. **Better UX** - Learn from their decades of iteration, start with best practices
5. **Free & Open Source** - No licensing fees, community-driven development
6. **Fast Performance** - Modern architecture, optimized for speed
7. **Easy Deployment** - Docker, one-command installation
8. **Cloud-Native** - Built for AWS/GCP/Azure from day one

### Next Steps

1. **Implement discussions system** (critical for collaboration)
2. **Build participants panel** (visibility and communication)
3. **Create task queue dashboard** (editor productivity)
4. **Add inline side panels** (reduce friction)
5. **Implement file management UI** (organized, clear versioning)
6. **Build decision workflow UI** (structured editorial decisions)

---

## References

- OJS 3.5 Release Documentation (June 2025)
- OJS Editorial Workflow Guide (Public Knowledge Project)
- ScholarOne Manuscripts Feature Overview (Clarivate)
- Editorial Manager Redesign Announcement (Aries Systems, 2024)
- Dashboard Design Patterns Research Paper (arXiv:2205.00757)
- Journal Management System Comparison Study (Publishing State, 2024)

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Author**: System Research & Analysis
**Purpose**: Guide implementation of journal management workflows based on industry-leading systems

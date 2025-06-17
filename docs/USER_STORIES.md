# User Stories & Personas - Luca AMA App

Detailed user stories and acceptance criteria for the AMA system.

## 👥 User Personas

### 🔧 Moderator
**Role**: Event organizer and admin
**Responsibilities**: Full system control, event management, content moderation
**Access Level**: Highest - can manage all aspects of events and questions

### 🎤 Presenter  
**Role**: The person answering questions in the AMA
**Responsibilities**: Managing questions during the session, marking answers
**Access Level**: High - can manage questions but not create/delete events

### 👤 User/Participant
**Role**: Event attendee who asks questions
**Responsibilities**: Asking questions, upvoting, participating in discussion
**Access Level**: Basic - can interact with questions within events they join

## 📋 Moderator Stories

### Event Management

#### Create Event
**Story**: As a moderator, I want to create an event so that I can moderate questions.

**Acceptance Criteria**:
- Can enter event name (required, max 100 characters)
- Can set optional open date
- Can set optional close date (must be after open date)
- Validation errors are displayed clearly
- I am automatically added as moderator
- Event is saved to database

**Workflow**:
1. Click 'New Event'
2. Fill in event details
3. Validate input
4. Save event
5. Auto-add as moderator

#### Generate Share Link
**Story**: As a moderator, I want to grant access to the event so that the right participants can join the AMA.

**Acceptance Criteria**:
- Can generate a unique share link
- Link can be copied to clipboard
- Link allows users to join the event
- Link can be regenerated if needed

#### Edit Event
**Story**: As a moderator, I want to edit an event so that I can update event details if plans change.

**Acceptance Criteria**:
- Can modify name, open date, close date
- Same validation as creation
- Changes are saved immediately
- Can cancel without saving

#### Delete Event
**Story**: As a moderator, I want to delete the event so that I can remove events that are no longer needed.

**Acceptance Criteria**:
- Shows confirmation dialog "Are you sure?"
- Event is permanently removed from database
- All associated questions are also deleted

### Question Management

#### Filter Questions
**Story**: As a moderator, I want to filter questions so that I can quickly find relevant or high-priority questions.

**Acceptance Criteria**:
- Can filter by keywords in question text
- Can filter by author name
- Can filter by answered status
- Can sort by vote count
- Filters work in combination
- Results update immediately

#### Mark as Answered
**Story**: As a moderator, I want to mark a question as answered so that it goes to the answered tab.

**Acceptance Criteria**:
- Can toggle answered status
- Question appears in "Answered" tab
- Question still visible in main list with status indicator
- Can unmark if needed

#### Add Presenter Notes
**Story**: As a moderator, I want to add presenter notes to a question so that I have context or guidance when answering.

**Acceptance Criteria**:
- Notes are only visible to moderators and presenters
- Notes are clearly distinguished in UI
- Can edit/update notes
- Optional AI summary is generated

#### Star Questions
**Story**: As a moderator, I want to add a star to a question so that I can highlight it as important.

**Acceptance Criteria**:
- Star toggle reflects immediately
- Starred questions appear in "Stars Only" tab
- Can remove star
- Visual indicator is clear

#### Stage Questions
**Story**: As a moderator, I want to stage a question so that it appears in the "Now Playing" section.

**Acceptance Criteria**:
- Only one question can be staged at a time
- Staging a new question unstages the previous one
- Staged question appears prominently in "Now Playing"
- Can unstage without staging another

#### View Grouped Questions
**Story**: As a moderator, I want to view grouped questions under a parent question so that I can manage them more easily.

**Acceptance Criteria**:
- Parent question displays [+] toggle
- Clicking [+] reveals grouped similar questions
- Can expand/collapse grouped view
- Grouped questions are visually indented

## 📋 Presenter Stories

### Event Viewing

#### View Event Details
**Story**: As a presenter, I want to view the event details so that I understand the context and schedule of the AMA.

**Acceptance Criteria**:
- Can see event name, open date, close date
- Can see list of moderators and participants
- Information is clearly displayed and up-to-date

#### View Question List
**Story**: As a presenter, I want to see the list of submitted questions so that I can prepare answers.

**Acceptance Criteria**:
- Can view all submitted questions
- Can see answered/starred status indicators
- Questions are sorted by relevance/votes

#### View Presenter Notes
**Story**: As a presenter, I want to see presenter notes on questions so that I can prepare answers.

**Acceptance Criteria**:
- Notes are visible only to presenters and moderators
- Notes are clearly distinguished from public content
- Can view notes added by moderators

### Question Management

#### Mark as Answered
**Story**: As a presenter, I want to mark a question as answered so that I can help manage the flow of the session.

**Acceptance Criteria**:
- Can mark/unmark questions as answered
- If question is staged, it's automatically unstaged when answered
- Question moves to answered tab
- Action is reflected immediately

#### Filter Questions
**Story**: As a presenter, I want to filter and search questions so that I can quickly find relevant ones to address.

**Acceptance Criteria**:
- Can filter by keyword, vote count, answered status
- Can search by keyword or author
- Filters work like moderator filters
- Results are relevant and fast

#### Star/Stage Questions
**Story**: As a presenter, I want to star and stage questions so that I can organize the discussion flow.

**Acceptance Criteria**:
- Same functionality as moderator
- Star toggle reflects immediately
- Staging follows same rules (one at a time)

## 📋 User Stories

### Authentication & Access

#### Join Event
**Story**: As a user, I want to join an event so that I can participate in the AMA.

**Acceptance Criteria**:
- Can accept invite shared by moderator
- Can access event via shared link
- Must be part of Microsoft tenant to access
- Validation error for non-tenant users

#### Login
**Story**: As a user, I want to log in so I can be authenticated.

**Acceptance Criteria**:
- Can enter credentials and be authenticated
- Proper error messages for invalid credentials
- Session persists across browser sessions
- Secure authentication flow

### Event Participation

#### View Event Details
**Story**: As a user, I want to view event details so that I know when and where to participate.

**Acceptance Criteria**:
- Can see event name
- Can see open and close dates
- Information is clearly presented

#### View Questions
**Story**: As a user, I want to see the list of submitted questions so that I can follow the discussion.

**Acceptance Criteria**:
- Can view all questions submitted to the event
- Can see who asked (or if anonymous)
- Can see answered status

#### View Answered Questions
**Story**: As a user, I want to see which questions are answered so that I can follow the discussion.

**Acceptance Criteria**:
- Answered questions are clearly marked
- Answered questions appear in separate tab
- Can still see in main list with indicator

### Question Interaction

#### Upvote Questions
**Story**: As a user, I want to upvote questions so that popular questions rise to the top.

**Acceptance Criteria**:
- Can upvote any question once
- Can remove upvote
- Cannot upvote own questions
- Vote count updates immediately

#### Search Questions
**Story**: As a user, I want to search for questions so that I can avoid duplicates.

**Acceptance Criteria**:
- Can search by keyword
- Results are relevant and fast
- Search works across question text

#### View Grouped Questions
**Story**: As a user, I want to see related questions grouped so that I can explore similar topics.

**Acceptance Criteria**:
- Grouped questions are expandable under parent
- [+] toggle shows/hides grouped questions
- Visual hierarchy is clear

### Question Management

#### Submit Question
**Story**: As a user, I want to submit a question so that I can participate in the discussion.

**Acceptance Criteria**:
- Can write and submit question text
- Can choose to be anonymous
- Question appears in list immediately
- Character limit validation

#### Edit Question
**Story**: As a user, I want to edit my question so that I can correct mistakes.

**Acceptance Criteria**:
- Can edit own questions before they're answered
- Cannot edit after moderator has answered
- Changes are saved immediately

#### Delete Question
**Story**: As a user, I want to delete my question so that I can remove it from the list.

**Acceptance Criteria**:
- Can delete own questions before they're answered
- Cannot delete after answered
- Confirmation dialog before deletion

#### View Staged Question
**Story**: As a user, I want to see the current question being discussed so that I can follow the live conversation.

**Acceptance Criteria**:
- Staged question appears in "Now Playing" section
- Section is prominently displayed
- Updates in real-time when moderator changes stage

## 🔄 Workflow Summaries

### Login Flow
1. User enters credentials
2. System validates against Microsoft tenant
3. JWT token issued on success
4. User redirected to dashboard

### Event Creation Flow
1. Moderator clicks "New Event"
2. Fills form with validation
3. Event saved to database
4. Moderator auto-added to event
5. Share link generated

### Question Submission Flow
1. User joins event via link
2. Writes question text
3. Chooses anonymous option
4. Submits question
5. Question appears in list for all users

### Question Management Flow
1. Moderator/presenter views question list
2. Filters/searches for relevant questions
3. Stars important questions
4. Stages question for discussion
5. Marks as answered when complete

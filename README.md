# Guia de Estudo Pro

Guia de Estudo Pro is a powerful, local-first, AI-driven study guide generator. It allows users to create, manage, and interact with custom learning paths on any subject, leveraging the power of large language models directly in the browser.

## Key Features

### 1. Guide Management (CRUD)
- **Create New Guides**: Easily start a new study guide by providing a title. The application uses AI to automatically generate a progressive and specific list of main topics.
- **View All Guides**: The main dashboard lists all your created guides, showing completion progress (percentage and topics completed/total).
- **Rename & Delete**: Full control over your guides with options to rename or delete them as needed.

### 2. AI-Powered Content Generation
- **Automatic Topic Generation**: Based on the guide's title, the AI suggests a list of 7-9 high-level topics, following instructional design best practices to ensure a logical progression.
- **Automatic Sub-topic Generation**: For each main topic, the AI can generate a more granular list of 6-9 sub-topics, covering prerequisites, core concepts, practical applications, and a mini-project.
- **Detailed Lesson Generation**: Generate a complete, in-depth lesson for any topic or sub-topic. The lesson is structured with clear learning objectives, prerequisites, fundamental concepts, guided examples, and practical exercises.
- **Bulk Generation**: Save time by generating all lessons for an entire guide or a specific branch of the knowledge tree in one go.

### 3. Interactive Study Environment
- **Knowledge Tree**: Navigate your study guide through a collapsible tree structure. This provides a clear overview of the entire curriculum.
- **Topic Completion Tracking**: Mark topics as "completed" to track your progress visually in the knowledge tree.
- **Interactive Q&A**: After generating a lesson, you can generate revision questions. Type your answer and have the AI evaluate it, providing constructive feedback.

### 4. Customization and Configuration
- **API Key Management**: Securely save your OpenAI API key in the browser's local storage. The key is never shared.
- **Model Selection**: Choose the OpenAI model that best suits your needs for both chat completions (e.g., `gpt-4o-mini`) and Text-to-Speech (e.g., `gpt-4o-mini-tts`).
- **Custom Prompts**: Power users can customize the prompts used for generating topics, sub-topics, lessons, and questions to tailor the AI's output to their specific needs.
- **Theme Switching**: Toggle between light and dark modes for a comfortable viewing experience.

### 5. Exporting
- **Multiple Formats**: Export your complete study guides into various formats:
    - **HTML**: A self-contained, styled web page with a table of contents.
    - **Markdown**: A structured text file, perfect for personal notes or version control.
    - **TXT**: A plain text version for maximum compatibility.
    - **JSON**: A complete dump of the guide's data structure, including all content and metadata, for backup or interoperability.

### 6. Audio Lessons (Text-to-Speech)
- **Downloadable Audio**: Generate and download an audio version of any lesson in MP3, WAV, or OGG format.
- **Voice and Code Options**: Configure the TTS voice and choose whether to include code blocks in the narration.

## How It Works

The application is a single `index.html` file that runs entirely in your web browser. It uses JavaScript to manage the application state, render the user interface, and interact with the OpenAI API. All data, including your study guides and API key, is stored locally in your browser's `localStorage`. This ensures privacy and makes the application fast and responsive.

## Getting Started

1.  Open the `index.html` file in a modern web browser.
2.  Navigate to the "Settings" page.
3.  Enter your OpenAI API key.
4.  Optionally, configure the models and custom prompts.
5.  Go back to "My Guides" and click "Create New Guide" to start learning!

## Usage

The application is designed to be intuitive. Here is a typical workflow:

### Creating a Guide
1.  From the **My Guides** dashboard, click the **Create New Guide** button.
2.  Enter a title for your subject (e.g., "History of Ancient Rome" or "Advanced JavaScript Concepts").
3.  The AI will generate the main topics and open the **Editor View**.

### Navigating the Editor
-   **Knowledge Tree** (Left Panel): This shows the structure of your guide.
    -   Click the `+` icon next to a topic to generate its sub-topics.
    -   Click the `▸` or `▾` icons to expand or collapse sub-topics.
    -   Double-click any topic title to rename it.
    -   Use the checkbox to mark a topic as complete.
-   **Study Area** (Right Panel): This is where you interact with the content.
    -   Select a topic from the tree to view it in the study area.

### Generating and Interacting with Lessons
1.  With a topic selected, click **Generate Lesson**. The AI will write a detailed lesson.
2.  Once the lesson is generated, you can:
    -   **Download Audio**: Get an MP3 audio version of the lesson.
    -   **Generate Questions**: Create a set of review questions based on the lesson.
    -   **Evaluate Answers**: Write your answer to a question and click **Evaluate Answer** to get AI-powered feedback.
3.  Use the **Bulk Generate Lessons** button to automatically create lessons for all topics in the guide or a specific branch.

### Exporting Your Guide
-   In the Editor View, use the **Export** buttons in the top toolbar to save your guide in HTML, Markdown, TXT, or JSON format.

## Author & Contact

-   **Jailton Fonseca**
-   **Location**: Brazil
-   **YouTube**: [www.youtube.com/@JailtonFonseca](https://www.youtube.com/@JailtonFonseca)
-   **Social Media**:
    -   Instagram: [@jailton_fon](https://instagram.com/jailton_fon)
    -   Facebook: [Jailton Fonseca](https://facebook.com/jailton.fonseca.507)
    -   TikTok: [@fonsecac41](https://tiktok.com/@fonsecac41)
    -   Twitch: [fonsecac41](https://twitch.tv/fonsecac41)

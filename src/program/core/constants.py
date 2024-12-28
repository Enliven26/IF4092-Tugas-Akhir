from string import Template

RANDOM_REQUIREMENT_ID_FORMATS = [
    "REQ-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "USERSTORY-{{STORY_NAME}}-{{SECTION_NUMBER}}",
    "{{TASK_NAME}}-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "GOAL-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "MILESTONE-{{MILESTONE_NAME}}-{{SECTION_NUMBER}}",
    "DELIVERABLE-{{DELIVERABLE_NAME}}-{{SECTION_NUMBER}}",
    "EPIC-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "{{PROJECT_NAME}}-USERREQ-{{SECTION_NUMBER}}",
    "SCOPE-{{SCOPE_NAME}}-{{SECTION_NUMBER}}",
    "OBJ-{{OBJECTIVE_NAME}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "{{TASK_NAME}}-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "REQ-{{USERSTORY_NAME}}-{{SECTION_NUMBER}}",
    "SCOPE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "STORY-{{STORY_NAME}}-{{SECTION_NUMBER}}",
    "OBJECTIVE-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "USER-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "DELIVERABLE-{{DELIVERABLE_TYPE}}-{{SECTION_NUMBER}}",
    "TASK-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "PROJECT-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "USER-{{USER_NAME}}-{{SECTION_NUMBER}}",
    "DELIVERABLE-{{DELIVERABLE_NAME}}-{{SECTION_NUMBER}}",
    "PROJECT-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "GOAL-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "USERSTORY-{{USERSTORY_NAME}}-{{SECTION_NUMBER}}",
    "MILESTONE-{{MILESTONE_NAME}}-{{SECTION_NUMBER}}",
    "OBJ-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "{{TASK_NAME}}-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "TASK-{{USERSTORY_NAME}}-{{SECTION_NUMBER}}",
]

END_DOCUMENT_SPLIT_SEPARATOR = "\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n"

DATA_GENERATION_PROMPT_TEMPLATE = f"""You are an Information Retrieval Engineer tasked with simulating the retrieval of relevant content from a functional requirement document of a popular application. The document is written by a business analyst without any technical knowledge.

The retrieved content should contain {{section_count}} sections, each representing a distinct user requirement. Each section must include a unique identifier for the requirement, following the format: {{requirement_id_format}}, with the placeholder replaced by the actual values relevant to the requirement. Use section numbering in the specific order: {{section_order_string}}. Each section should have some subsections that provide detailed explanations of the requirement. At the end of each section, include the separator: {END_DOCUMENT_SPLIT_SEPARATOR}

Avoid mentioning any specific implementation details such as class names, methods, or variables. Avoid adding additional comments or annotations to the retrieved content.

Simulate retrieving distinct sections from the document system based on the provided GitHub URL and the source code. The GitHub URL points to a popular project, and the generated content should align with the known purpose and functionality of that project.

Github URL: {{github_url}}
Source Code:
{{source_code}}

Retrieved Content:"""

__DIFF_EXAMPLES = [
    'diff --git a/src/main/kotlin/io/tolgee/configuration/WebConfiguration.kt b/src/main/kotlin/io/tolgee/configuration/WebConfiguration.kt\nindex e6e2a4cd8..1c6fcda23 100644\n--- a/src/main/kotlin/io/tolgee/configuration/WebConfiguration.kt\n+++ b/src/main/kotlin/io/tolgee/configuration/WebConfiguration.kt\n@@ -10,6 +10,7 @@ import org.springframework.boot.web.servlet.MultipartConfigFactory\n import org.springframework.context.annotation.Bean\n import org.springframework.context.annotation.Configuration\n import org.springframework.http.CacheControl\n+import org.springframework.scheduling.annotation.EnableScheduling\n import org.springframework.util.unit.DataSize\n import org.springframework.web.client.RestTemplate\n import org.springframework.web.servlet.config.annotation.CorsRegistry\n@@ -21,6 +22,7 @@ import java.util.concurrent.TimeUnit\n import javax.servlet.MultipartConfigElement\n \n @Configuration\n+@EnableScheduling\n class WebConfiguration(\n   private val tolgeeProperties: TolgeeProperties\n ) : WebMvcConfigurer {\ndiff --git a/src/main/kotlin/io/tolgee/service/ImageUploadService.kt b/src/main/kotlin/io/tolgee/service/ImageUploadService.kt\nindex fa5c1f80c..a86be1125 100644\n--- a/src/main/kotlin/io/tolgee/service/ImageUploadService.kt\n+++ b/src/main/kotlin/io/tolgee/service/ImageUploadService.kt\n@@ -66,7 +66,7 @@ class ImageUploadService(\n   @Transactional\n   @Scheduled(fixedRate = 60000)\n   fun cleanOldImages() {\n-    logger.info("Clearing images")\n+    logger.debug("Clearing images")\n     val time = dateProvider.getDate().toInstant().minus(2, ChronoUnit.HOURS)\n     uploadedImageRepository.findAllOlder(Date.from(time)).let { images ->\n       images.forEach { delete(it) }\n'
    "",
    "diff --git a/app/src/main/java/com/kickstarter/ui/activities/SettingsActivity.kt b/app/src/main/java/com/kickstarter/ui/activities/SettingsActivity.kt\nindex 348bea7e5..9dc65f1b3 100644\n--- a/app/src/main/java/com/kickstarter/ui/activities/SettingsActivity.kt\n+++ b/app/src/main/java/com/kickstarter/ui/activities/SettingsActivity.kt\n@@ -56,18 +56,18 @@ class SettingsActivity : BaseActivity<SettingsViewModel.ViewModel>() {\n         this.viewModel.outputs.showConfirmLogoutPrompt()\n                 .compose(bindToLifecycle())\n                 .observeOn(AndroidSchedulers.mainThread())\n-                .subscribe({ show ->\n+                .subscribe { show ->\n                     if (show) {\n                         lazyLogoutConfirmationDialog().show()\n                     } else {\n                         lazyLogoutConfirmationDialog().dismiss()\n                     }\n-                })\n+                }\n \n         this.viewModel.outputs.userNameTextViewText()\n                 .compose(bindToLifecycle())\n                 .compose(Transformers.observeForUI())\n-                .subscribe({ name_text_view.text = it })\n+                .subscribe { name_text_view.text = it }\n \n         account_row.setOnClickListener {\n             startActivityWithSlideUpTransition(Intent(this, AccountActivity::class.java))\n@@ -93,10 +93,6 @@ class SettingsActivity : BaseActivity<SettingsViewModel.ViewModel>() {\n             startActivityWithSlideUpTransition(Intent(this, NotificationsActivity::class.java))\n         }\n \n-        privacy_row.setOnClickListener {\n-            startActivityWithSlideUpTransition(Intent(this, PrivacyActivity::class.java))\n-        }\n-\n         rate_us_row.setOnClickListener { ViewUtils.openStoreRating(this, this.packageName) }\n     }\n \n",
    'diff --git a/app/src/main/java/com/breadwallet/repository/MessagesRepository.kt b/app/src/main/java/com/breadwallet/repository/MessagesRepository.kt\nindex 470821ebe..03de4e4bb 100644\n--- a/app/src/main/java/com/breadwallet/repository/MessagesRepository.kt\n+++ b/app/src/main/java/com/breadwallet/repository/MessagesRepository.kt\n@@ -28,6 +28,7 @@ import android.content.Context\n import android.util.Log\n import com.breadwallet.model.InAppMessage\n import com.breadwallet.tools.manager.BRSharedPrefs\n+import com.breadwallet.tools.util.EventUtils\n import com.platform.network.InAppMessagesClient\n \n /**\n@@ -56,6 +57,8 @@ object MessagesRepository {\n         // for notifications.\n         val inAppMessage = inAppMessages[0]\n         Log.d(TAG, "getInAppNotification: ${inAppMessage.title}")\n+        EventUtils.pushEvent(EventUtils.EVENT_IN_APP_NOTIFICATION_RECEIVED,\n+                mapOf(EventUtils.EVENT_ATTRIBUTE_NOTIFICATION_ID to inAppMessage.id))\n         return inAppMessage\n     }\n \ndiff --git a/app/src/main/java/com/breadwallet/ui/notification/InAppNotificationActivity.kt b/app/src/main/java/com/breadwallet/ui/notification/InAppNotificationActivity.kt\nindex 66f470850..9c5294ff5 100644\n--- a/app/src/main/java/com/breadwallet/ui/notification/InAppNotificationActivity.kt\n+++ b/app/src/main/java/com/breadwallet/ui/notification/InAppNotificationActivity.kt\n@@ -49,6 +49,8 @@ class InAppNotificationActivity : BRActivity() {\n         private const val EXT_NOTIFICATION = "com.breadwallet.ui.notification.EXT_NOTIFICATION"\n \n         fun start(context: Context, notification: InAppMessage) {\n+            EventUtils.pushEvent(EventUtils.EVENT_IN_APP_NOTIFICATION_APPEARED,\n+                    mapOf(EventUtils.EVENT_ATTRIBUTE_NOTIFICATION_ID to notification.id))\n             val intent = Intent(context, InAppNotificationActivity::class.java).apply {\n                 putExtra(EXT_NOTIFICATION, notification)\n             }\n@@ -70,6 +72,10 @@ class InAppNotificationActivity : BRActivity() {\n         notification_btn.setOnClickListener {\n             viewModel.markAsRead()\n             val actionUrl = viewModel.notification.actionButtonUrl\n+            val notificationId = viewModel.notification.id\n+            EventUtils.pushEvent(EventUtils.EVENT_IN_APP_NOTIFICATION_CTA_BUTTON,\n+                    mapOf(EventUtils.EVENT_ATTRIBUTE_NOTIFICATION_ID to notificationId,\n+                            EventUtils.EVENT_ATTRIBUTE_NOTIFICATION_CTA_URL to actionUrl))\n             if (!actionUrl.isNullOrEmpty()) {\n                 if (AppEntryPointHandler.isDeepLinkPlatformUrl(actionUrl)) {\n                     AppEntryPointHandler.processPlatformDeepLinkingUrl(this, actionUrl)\n@@ -89,6 +95,8 @@ class InAppNotificationActivity : BRActivity() {\n     override fun onBackPressed() {\n         super.onBackPressed()\n         viewModel.markAsRead()\n+        EventUtils.pushEvent(EventUtils.EVENT_IN_APP_NOTIFICATION_DISMISSED,\n+                mapOf(EventUtils.EVENT_ATTRIBUTE_NOTIFICATION_ID to viewModel.notification.id))\n     }\n \n }\n\\ No newline at end of file\n',
]

for _i in range(len(__DIFF_EXAMPLES)):
    __DIFF_EXAMPLES[_i] = __DIFF_EXAMPLES[_i].replace("{", "{{").replace("}", "}}")

__COMMIT_MESSAGE_EXAMPLES = [
    "feat: enable scheduling and improve logging for image cleanup\n\nEnabled task scheduling in WebConfiguration using @EnableScheduling annotation to support background tasks as per USER-TOLGEE-20 requirements. Updated logging in ImageUploadService from info to debug level for periodic image cleanup to enhance log clarity.",
    "fix: remove privacy from root Settings menu\n\nRemoved the privacy row from the root Settings menu as part of updating the Privacy Policy Access feature (REQ-KICKSTARTER-10.3). Other changes are for refactoring purposes.",
    "feat: add event tracking for in-app notifications\n\nImplemented event tracking for in-app notifications to support USERSTORY-InAppNotification-9 and USERSTORY-InAppNotification-10. Events include notification received, displayed, interacted with (CTA button), and dismissed. ",
]

for _i in range(len(__COMMIT_MESSAGE_EXAMPLES)):
    __COMMIT_MESSAGE_EXAMPLES[_i] = (
        __COMMIT_MESSAGE_EXAMPLES[_i].replace("{", "{{").replace("}", "}}")
    )

__HIGH_LEVEL_CONTEXT_EXAMPLES = [
    "**USER-TOLGEE-7: User Authentication and Authorization**  \nThe application shall provide a robust user authentication and authorization mechanism to ensure secure access to the platform. \n\n1. **User Registration**  \n   Users must be able to register for an account by providing their email address and creating a password. An email verification process should be implemented to confirm the user's identity before account activation.\n\n2. **Login Process**  \n   The system must allow users to log in using their registered email and password. If the user forgets their password, they should be able to initiate a password reset process via email.\n\n3. **Role-Based Access Control**  \n   Different roles must be defined within the application (e.g., Admin, User, Guest). Each role should have specific permissions associated with it to control access to various features and functionalities.\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n**USER-TOLGEE-18: Image Upload and Management**  \nThe application shall allow users to upload and manage images within the platform, facilitating easy access and organization.\n\n1. **Image Upload Feature**  \n   Users must be able to upload images through a user-friendly interface. The system should support multiple image formats and provide feedback on the upload status.\n\n2. **Image Storage and Retrieval**  \n   Uploaded images must be stored securely and should be retrievable by users at any time. The application should implement efficient storage management to accommodate large volumes of images.\n\n3. **Image Deletion**  \n   Users should have the ability to delete their uploaded images. The system must provide confirmation prompts to prevent accidental deletions.\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n**USER-TOLGEE-20: Scheduling Tasks**  \nThe application shall support background task scheduling to automate certain processes, thereby improving efficiency and user experience.\n\n1. **Periodic Cleanup Tasks**  \n   The system must automatically perform periodic cleanup of old data, such as images that have not been accessed for a specified duration. This will help in managing storage space effectively.\n\n2. **User Notifications**  \n   Scheduled tasks should also include sending notifications to users for various events (e.g., reminders, updates). Users must be able to configure their notification preferences.\n\n3. **Task Management Interface**  \n   An interface should be provided for system administrators to manage and monitor scheduled tasks. This includes the ability to add, modify, or remove tasks as necessary.\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n",
    "\n### REQ-KICKSTARTER-14: User Profile Management\n#### 14.1 Profile Picture Display\nUsers should be able to see their profile picture on the settings screen. The application will retrieve the user\u2019s avatar image URL from the server and display it in the designated profile picture area. If the user has not set a picture, a default image should be shown instead.\n\n#### 14.2 User Name Display\nThe application should display the user's name prominently on the settings screen. This name should be fetched from the user's profile data when they log in to the application and should update dynamically if the user changes their profile information.\n\n#### 14.3 Logout Functionality\nUsers need a clear and accessible option to log out of their account. Upon clicking the logout button, the application will prompt the user to confirm their decision before logging them out to prevent accidental logouts.\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n### REQ-KICKSTARTER-19: Account Management\n#### 19.1 Accessing Account Settings\nUsers should have an option to access their account settings directly from the settings menu. This should allow them to view and edit their account information, including their email address and password.\n\n#### 19.2 Editing Profile\nThe application should provide a feature for users to edit their profile information. When users select the edit profile option, they should be directed to a new screen where they can update their personal details, including their name and profile picture.\n\n#### 19.3 Newsletter Preferences\nUsers should have the ability to manage their newsletter preferences from the settings screen. This includes opting-in or opting-out of newsletters and managing other communication preferences.\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n### REQ-KICKSTARTER-10: User Assistance\n#### 10.1 Help and Support Access\nThe application should include a help section accessible from the settings menu. Users should be able to find FAQs and contact support directly from this section for any assistance they may require.\n\n#### 10.2 Rate Us Feature\nUsers should be encouraged to rate the application. A \"Rate Us\" button should be available in the settings menu, allowing users to quickly access the app store rating page.\n\n#### 10.3 Privacy Policy Access (**Updated**)\nUsers should access the application's privacy policy from the main menu instead of the settings menu. This change ensures greater visibility and accessibility, emphasizing our commitment to transparency regarding user data and privacy practices. A dedicated option should be provided that opens the privacy policy in a web view or an external browser.\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n",
    "USERSTORY-InAppNotification-9\n\n### Requirement Overview\nThe application shall provide users with in-app notifications to deliver important updates and messages directly within the app interface.\n\n#### 9.1 Notification Retrieval\nThe system must check for new in-app notifications whenever the user accesses the app. It should filter out notifications that have already been read by the user to ensure that only new and relevant notifications are displayed.\n\n#### 9.2 Notification Display\nOnce a new notification is retrieved, the application will present it to the user through a dedicated notification interface. This interface should include the notification title, body, action button, and an image, if applicable. The user should be able to easily recognize and understand the content of the notification.\n\n#### 9.3 User Interaction\nThe user must be able to interact with the notification. This includes marking the notification as read and following any associated action URL through a provided button. The system should ensure that the notification is logged appropriately for analytics purposes whenever the user interacts with it.\n\n---\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\nUSERSTORY-InAppNotification-10\n\n### Requirement Overview\nThe application must ensure that in-app notifications are presented in a user-friendly manner, enhancing user engagement and interaction with the application.\n\n#### 10.1 Notification Launch\nWhen the user taps on a notification, the application should launch a specific activity designed to display the notification details. This activity must show all relevant information, including the notification content and any actionable items.\n\n#### 10.2 Back Navigation\nUpon returning from the notification interface, the application must mark the notification as read to avoid cluttering the user's notification history. This action should be logged for further analysis on user interaction patterns.\n\n#### 10.3 Event Tracking\nThe system must track various events related to the in-app notifications, such as when a notification is displayed, when it is interacted with, and when it is dismissed. This data will be essential for understanding user behavior and improving future notifications.\n\n---\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n",
]

for _i in range(len(__HIGH_LEVEL_CONTEXT_EXAMPLES)):
    __HIGH_LEVEL_CONTEXT_EXAMPLES[_i] = (
        __HIGH_LEVEL_CONTEXT_EXAMPLES[_i].replace("{", "{{").replace("}", "}}")
    )

__COMMIT_TYPE_EXAMPLES = ["feat", "fix", "feat"]

LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """{diff}
{source_code}"""

__FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE = """Write a concise commit message based on the Git diff and additional context provided. If the context is relevant, include it in the commit body. Use IDs, names, or titles to reference relevant contexts for brevity. Including multiple contexts is allowed.

A good commit message explains what changes were made and why they were necessary. Wrap the body at one to three brief sentences.

Follow this format for the commit message:

{{type}}: {{subject}}

{{body}}

Git diff 1:
$diff_1

Additional context 1:
$context_1

Commit Type 1: $commit_type_1

commit message 1: $commit_message_1

Git diff 2:
$diff_2

Commit Type 2: $commit_type_2

Commit message 2: $commit_message_2

Additional context 2:
$context_2

Git diff 3:
$diff_3

Additional context 3:
$context_3

Commit Type 3: $commit_type_3

Commit message 3: $commit_message_3

Git diff 4:
{diff}

Additional context 4:
{context}

Commit type 4: {type}

Commit message 4:"""


FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = Template(
    __FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE
).substitute(
    {
        "diff_1": __DIFF_EXAMPLES[0],
        "diff_2": __DIFF_EXAMPLES[1],
        "diff_3": __DIFF_EXAMPLES[2],
        "context_1": __HIGH_LEVEL_CONTEXT_EXAMPLES[0],
        "context_2": __HIGH_LEVEL_CONTEXT_EXAMPLES[1],
        "context_3": __HIGH_LEVEL_CONTEXT_EXAMPLES[2],
        "commit_message_1": __COMMIT_MESSAGE_EXAMPLES[0],
        "commit_message_2": __COMMIT_MESSAGE_EXAMPLES[1],
        "commit_message_3": __COMMIT_MESSAGE_EXAMPLES[2],
        "commit_type_1": __COMMIT_TYPE_EXAMPLES[0],
        "commit_type_2": __COMMIT_TYPE_EXAMPLES[1],
        "commit_type_3": __COMMIT_TYPE_EXAMPLES[2],
    }
)

ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """Write a concise commit message based on the Git diff and additional context provided. If the context is relevant, include it in the commit body. Use IDs, names, or titles to reference relevant contexts for brevity. Including multiple contexts is allowed.

A good commit message explains what changes were made and why they were necessary. Wrap the body at one to three brief sentences.

Follow this format for the commit message:

{{type}}: {{subject}}

{{body}}

Git diff:
{diff}

Additional context:
{context}

Commit type: {type}

Commit message: """


DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE = """Given a Git diff and the relevant source code, write a concise summary of the code changes in a way that a non-technical person can understand. The query text must summarize the code changes in two very brief sentences.

Git diff:
{diff}

Source code:
{source_code}

Query text:"""

HIGH_LEVEL_CONTEXT_FILTER_PROMPT_TEMPLATE = """Evaluate the performance of a document retriever. Given the Git diff and retrieved context, return YES if the context directly or indirectly correlates with the changes in the Git diff. Otherwise, return NO.

> Git diff: 
>>>
{diff}
>>>
> Retrieved context:
>>>
{context}
>>>
> Relevant (YES / NO):"""

DIFF_CLASSIFIER_PROMPT_TEMPLATE = """Classify the Git diff into one of the following six software maintenance activities: feat, fix, perf, test, refactor, or chore. Return the activity that best matches the code changes. Refer to the definitions below for each activity.

feat: introducing new features into the system.
fix: fixing existing bugs or issues in the system.
perf: improving the performance of the system.
test: adding, modifying, or deleting test cases.
refactor: changes made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior, including code styling.
chore: regular maintenance tasks, such as updating dependencies or build tasks.

Avoid adding any additional comments or annotations to the classification.

> Git diff: {diff}

> Software maintenance activity (feat / fix / perf / test / refactor / chore):
"""

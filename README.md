# WebNews

Nanna News is an intensive information carrier built with passion by students from various majors at NJU. It strives to collect and organize information at the lowest possible cost and publish it in an easy-to-read format, aiming to break down information barriers and enhance the well-being of fellow students.

WebNews is the web platform for editing and publishing Nanna News.

Our first newsletter was sent on May 23, 2024, using LaTeX. As of March 13, 2025, LaTeX publishing was discontinued, and we transitioned to using Typst for publishing. See [this repository](https://github.com/nik-nul/Nanna_News---LTS) for the previous publishing workflow and newsletters.

Within NJU, this website began its trial phase within club groups on March 14, 2025. It was adopted for all groups and messages starting March 20, 2025. Finally, on May 20, 2025, we stopped converting messages to LaTeX and moved to an entirely Typst-based workflow.

We are also assisting OUC in establishing its own news service. Their trial period commenced on April 16, 2025, with official publishing starting on April 23, 2025. They began utilizing the Deadline Table feature on May 13, 2025.

If you are interested in creating your own university news group to help more students, please contact me at [231220103@smail.nju.edu.cn](mailto:231220103@smail.nju.edu.cn). I can host a website for you or assist you in deploying this website on your own server.

## Usage and Deployment

1.  **Set up a virtual environment:** Create a virtual environment using your preferred method.
2.  **Install dependencies:** Activate the virtual environment and install the required packages using:
    ```bash
    pip install -r requirements.txt
    ```
    This project was originally developed, tested, and deployed using Python 3.10.12 and the latest available versions of the dependencies at that time. However, it should, in principle, work correctly with most recent Python versions.

3.  **Configuration:**
    * Set the `app.secret_key` in your application configuration.
    * Define your `EDITOR_LIST` and `ADMIN_LIST` to specify user roles.
    * Configure the parameters for `app.run` within the `if __name__ == '__main__':` block to suit your server's web environment.
    * Download the Typst binary from the [official Typst repository](https://github.com/typst/typst) and place it in the project's root directory.
    * Directly run `python3 main.py` is not recommended by flask. You can refer to related tutorial for better way to deploy.

Once these steps are completed, the application should be ready to run.

**User Registration:**
For security reasons, user registration is restricted by default. If needed, you can temporarily or permanently disable this restriction by commenting out the `@admin_required` decorator above the `register()` function in the relevant route file.

Other permission controls are managed similarly, using decorators that can be adjusted as needed.

## Publishing Workflow

The general workflow involves recruiting members, gathering information, and utilizing the platform's features for drafting, reviewing, and publishing.

1.  **Team & Source Setup:**
    * Recruit members for the newsletter team.
    * Identify and list key university information channels (e.g., official website, WeChat official accounts, notice boards).
    * Assign team members to regularly monitor these channels for new information.

2.  **Uploading News Items:**
    * **Link-based:** If you find a news link, paste it into the system. The platform will attempt to fetch the title and check for duplicates. Successfully added links will appear on the homepage as items pending processing.
    * **Image-based:** Use the image upload feature for news primarily conveyed through images.
    * **Text-based:** For news without a direct link or image, submit it as a plain text entry.

3.  **Drafting Content:**
    Team members can collectively process pending items (e.g., during a set evening review time). When drafting:
    * **Deadlines:** For events with a deadline, use the "Deadline" option. Enter a concise title for display in the Deadline Table and specify the deadline date.
    * **Conciseness:** Write brief summaries. The original source link will be automatically included, allowing readers to get the gist. Full details can be accessed via the hyperlink or QR code (if provided with the source).
    * **Tagging:** Utilize tags to categorize entries. University-wide events, often being high priority, might be displayed more prominently. Proper categorization enhances the newsletter's organization, especially with numerous items.
    * **Editing Lock:** To prevent conflicts, an item is locked for 15 minutes when a user begins editing. The lock is released upon submission or cancellation. If the timer expires, the item may become available to others. Avoid keeping items open for long periods without active editing.

4.  **Reviewing:**
    * After drafting, items move to a Pending Review state.
    * The review interface is similar to the drafting one. Reviewers can modify content and click "Modify," or approve it by clicking "Approve".
    * Users cannot approve their own submissions or items where they were the last to make modifications.

5.  **Publishing (Admin Task):**
    * Users with `EDITOR` privileges can access the `/admin` route.
    * Here, they can select reviewed items, assign a publication date, and click "Publish".
    * Published items are then removed from the main list of pending items.

6.  **Previewing:**
    * A "Preview" button (typically on the main or admin page) allows for checking the newsletter's appearance before final generation.
    * If issues are identified, an "Edit" button often allows for returning to the review/editing interface for that item.

7.  **Generating the Newsletter (Admin Task):**
    * `EDITOR`s can access the `/publish` route.
    * On the left panel, select the desired date and click "Fetch" to retrieve the day's data.
    * Click "Submit" to generate the PDF on the right.
    * **Parameters:**
        * `date`: The publication date for the newsletter.
        * `no`: The issue number of the newsletter.
        * Vertical spacing options (e.g., parameters with `-v`): These control the vertical whitespace (in line units) below each section. Use a negative value to reduce space or a positive value if sections overlap.
    * After adjusting parameters, click "Submit" again to regenerate and preview the layout.
    * Download the finalized PDF for distribution. Images can be exported from the PDF using standard PDF editing tools if necessary.

## Development

This website is currently under active development. Planned features include:

-   [ ] Deployment to GitHub Pages
-   [x]  Email delivery system ([#15](https://github.com/nik-nul/WebNews/pull/15))
-   [ ] RSS feed service

PRs are welcome! To avoid duplicate work, please open a draft pull request or an issue to discuss any new features you'd like to contribute before starting development.

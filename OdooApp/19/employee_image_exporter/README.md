# Advanced Employee Image Exporter for Odoo 18

This module provides a powerful and flexible tool to export employee profile pictures as a single ZIP archive, offering advanced filtering, custom file naming, and on-the-fly image processing.

## Key Features

*   **Advanced Filtering:** Select employees using a standard Odoo domain filter.
*   **Custom Naming:** Define a custom file naming convention using employee field placeholders.
*   **Image Processing:** Options to resize and convert images to different formats (e.g., JPEG, PNG) during export.
*   **Security:** Controlled access via a dedicated user group.

## Usage

1.  **Access the Wizard:**
    *   Navigate to the **Employees** app.
    *   Go to **Configuration** > **Export Employee Images** (or use the action button on the employee list view).

2.  **Configure Export:**

    *   **Employee Selection:**
        *   Enter an Odoo domain to filter the employees you wish to export.
        *   *Example:* `[('department_id.name', '=', 'Sales')]` to export only employees in the Sales department. Leave as `[]` to export all employees.

    *   **File Naming Convention:**
        *   Define your desired filename format using placeholders:
            *   `[name]`: Employee's full name.
            *   `[id_number]`: Employee's Identification Number (`identification_id`).
            *   `[record_id]`: Employee's database ID (`id`).
            *   `[job_title]`: Employee's Job Position title (`job_title`).
            *   `[department_name]`: Employee's Department name.
        *   *Example:* `[department_name]_[name]_[id_number]`

    *   **Image Processing Options:**
        *   **Resize Width/Height:** Enter pixel values to resize the images. If only one is provided, the image will be resized proportionally. Leave both as 0 to keep the original size.
        *   **Output Format:** Choose between `PNG` (lossless quality) or `JPEG` (compressed, smaller file size).

3.  **Generate and Download:**
    *   Click the **Generate Zip File** button.
    *   Once processed, the button will change to **Download Zip**. Click it to download the `employee_images_export.zip` file.

## Technical Details

*   **Models:** `employee.image.export.wizard` (Transient Model)
*   **Security Group:** `employee_image_exporter.group_employee_image_exporter`
*   **Dependencies:** `hr`, `base`
*   **External Libraries:** Uses the standard Python `zipfile` and `Pillow` (PIL) library for image processing, which is typically available in Odoo environments.

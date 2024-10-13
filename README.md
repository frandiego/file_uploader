# Automatic Photo Sorter & Uploader to PCloud
## Overview
This project automates the process of sorting photos taken with a camera by year and month, and then uploads them to 
PCloud. The program scans a directory for new images, organizes them into folders based on the date they were taken, 
and securely uploads them to the PCloud cloud storage service.
## Features
- **Automatic Sorting**: Organizes photos into subfolders by year and month based on the image’s metadata (creation 
date).
- **PCloud Integration**: Automatically uploads sorted photos to your PCloud account.
- **Efficient & Fast**: Designed to handle large batches of photos.
  
## Requirements
- Python 3.x
- `requests` library
- `os` and `shutil` for file operations
- PCloud API access (you will need to generate an authentication token)
## Installation
1. Clone this repository:
   \`\`\`bash
   git clone https://github.com/yourusername/photo-sorter-uploader.git
   cd photo-sorter-uploader
   \`\`\`
2. Install the required Python packages:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
3. Set up PCloud API authentication by adding your token to the `.env` file:
   \`\`\`bash
   PCloud_TOKEN=your_pcloud_token
   \`\`\`
## Usage
1. Place your camera's photos in the designated `input/` folder.
2. Run the script to automatically sort and upload the photos:
   \`\`\`bash
   python main.py
   \`\`\`
   The photos will be moved into `sorted_photos/` organized by year and month and uploaded to PCloud.
## File Structure
- **input/**: Directory where you place your unsorted photos.
- **sorted_photos/**: Directory where photos are organized after processing.
- **upload.py**: Handles the upload to PCloud.
- **sort.py**: Sorts the photos based on EXIF data (creation date).
## Contributing
Feel free to submit issues or pull requests to improve the project!
## License
This project is licensed under the MIT License.



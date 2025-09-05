# BatchFontCollector
Python script that collects fonts from multiple subtitle files, organizes them by episode, and reports missing fonts.

## Requirements
- Python 3.8+  
- [FontCollector](https://github.com/moi15moi/FontCollector) (Make sure that the Python `Scripts` folder is included in your system's environment variables.)

## Features
- Processes multiple `.ass` subtitle files in batch.  
- Collects all fonts required by each subtitle file.  
- Organizes fonts into folders per episode.  
- Logs the extraction process (`process.log`).  
- Reports missing fonts (`missing_fonts.log`). 

## Usage
1. Open a terminal
2. Navigate to the folder containing your `batch_font_collector.py` script.
3. Run the script with the path to your subtitles folder:

```bash
python batch_font_collector.py "path to subtitles"

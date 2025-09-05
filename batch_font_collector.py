import subprocess
import os
import sys
import time
import concurrent.futures
import threading

input_folder = sys.argv[1]
output_folder = os.path.join(input_folder, "fonts")
output_file = os.path.join(input_folder, "process.log")
errors_file = os.path.join(input_folder, "missing_fonts.log")

#additional_fonts_folder = r"C:\Users\path\additional_fonts"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

files = sorted([f for f in os.listdir(input_folder)
                if os.path.isfile(os.path.join(input_folder, f)) and f.endswith(".ass")])

start_time = time.time()
current_file = 0
total_files = len(files)
done = False

lock = threading.Lock()
max_concurrent_files = 6
semaphore = threading.Semaphore(max_concurrent_files)


file_logs = {}

def process_file(file, semaphore):
    global current_file
    with semaphore:
        input_file = os.path.join(input_folder, file)
        font_folder = os.path.join(output_folder, os.path.splitext(file)[0])
        
        #"--exclude-system-fonts" 
        #"--additional-fonts-recursive", additional_fonts_folder
        process = subprocess.Popen(
            ["FontCollector", "-i", input_file, "-o", font_folder],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = process.communicate()

        with lock:
            file_logs[file] = (out.decode('utf-8', errors='replace'),
                               err.decode('utf-8', errors='replace'))
            current_file += 1

def show_progress():
    spinner = ['|', '/', '-', '\\']
    while not done:
        minutes, seconds = divmod(int(time.time() - start_time), 60)
        time_display = f"{minutes} minute(s) {seconds} seconds" if minutes > 0 else f"{seconds} seconds"
        progress = int((current_file / total_files) * 100)
        sys.stdout.write(f"\rProcessing: {progress}% {spinner[progress % 4]} Time: {time_display}")
        sys.stdout.flush()
        time.sleep(0.5)

progress_thread = threading.Thread(target=show_progress)
progress_thread.start()

with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_files) as executor:
    futures = [executor.submit(process_file, file, semaphore) for file in files]

concurrent.futures.wait(futures)

done = True
progress_thread.join()

elapsed_time = time.time() - start_time
minutes, seconds = divmod(int(elapsed_time), 60)
time_display = f"{minutes} minute(s) {seconds} seconds" if minutes > 0 else f"{seconds} second(s)"
print(f"\rProcessing: 100% ✓ Time: {time_display}")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("Execution log:\n\n")
    for file in files:
        out, err = file_logs.get(file, ("", ""))
        f.write(f"Fonts extracted for {file}\n")
        if out.strip():
            f.write(out + "\n")
        if err.strip():
            f.write(err + "\n")
        f.write("\n")

def clean_info_txt(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    filtered_blocks = []
    current_block = []
    errors_in_block = []
    episodes_with_errors = []

    def append_block():
        if current_block and errors_in_block:
            filtered_blocks.append(current_block[0])
            filtered_blocks.extend(errors_in_block)
            filtered_blocks.append("\n\n")
            episodes_with_errors.append(current_block[0].replace("Fonts extracted for ", "").strip())

    for line in lines:
        if line.startswith("Fonts extracted for"):
            append_block()
            current_block = [line]
            errors_in_block = []
        else:
            if line.startswith("ERROR - "):
                errors_in_block.append(line)

    append_block()

    if filtered_blocks:
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in filtered_blocks:
                if not line.endswith("\n"):
                    line += "\n"
                f.write(line)
        print("\nErrors were found in the following episodes:")
        for ep in episodes_with_errors:
            print(f" - {ep}")
        print(f"\nSaved to:\n{output_path}\n")
    else:
        print("\nAll files were processed successfully!\n")

clean_info_txt(output_file, errors_file)

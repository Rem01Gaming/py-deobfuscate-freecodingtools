import os, subprocess, sys

def check_python() -> bool:
    """Check if Python 2 is installed on the system."""
    try:
        subprocess.run(['python2', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def python_exec(script_path: str) -> str:
    """Run a Python 2 script and capture its output."""
    try:
        result = subprocess.run(['python2', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error executing {script_path}: {result.stderr}", file=sys.stderr)
        return result.stdout
    except FileNotFoundError as e:
        print(f"Error executing {script_path}: {str(e)}", file=sys.stderr)
        sys.exit(1)

def replace_exec(content: str) -> str:
    """
    Replace 'exec' with 'print' in the script content."""
    if 'exec' not in content:
        print("Error: 'exec' not found in the script content.", file=sys.stderr)
        sys.exit(1)
    return content.replace('exec', 'print')

def deobfuscate_layer(enc: str) -> str:
    """Writing a new script for deobfuscate a single layer by decoding base64 and decompressing with zlib."""
    return (
        "_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));"
        "print((_)(b'{0}'))".format(enc)
    )

def deobfuscate_script(filepath: str) -> None:
    """Main function to handle deobfuscation of a script."""
    with open(filepath, 'r') as f:
        script_content = f.read()

    # Replace 'exec' with 'print'
    script_content = replace_exec(script_content)

    # Write the modified content to a temporary file
    temp_file_1 = '1.tmp'
    with open(temp_file_1, 'w') as f:
        f.write(script_content)

    # Run the modified script and capture the output
    temp_file_2 = '2.tmp'
    with open(temp_file_2, 'w') as f:
        f.write(python_exec(temp_file_1))

    layer = 2
    while True:
        with open(temp_file_2, 'r') as f:
            content = f.read()

        if 'exec((_)' in content:
            new_script = deobfuscate_layer(content.split("'")[1])

            with open(temp_file_2, 'w') as f:
                f.write(new_script)

            result = python_exec(temp_file_2)
            with open(temp_file_2, 'w') as f:
                f.write(result)

            print(f"Deobfuscating layer {layer}...", end="\r")
            layer += 1
        else:
            os.remove(temp_file_1)
            output_file = f'{filepath}.dec'
            os.rename(temp_file_2, output_file)
            print(f"Deobfuscated script saved to: {output_file}")
            break

def main() -> None:
    """Main function for script execution."""
    if not check_python():
        sys.exit(1)

    if len(sys.argv) != 2:
        script_name = os.path.basename(sys.argv[0])
        print(f"Usage: python3 {script_name} <script_path>", file=sys.stderr)
        sys.exit(1)

    script_path: str = sys.argv[1]
    if not os.path.isfile(script_path):
        print(f"Script {script_path} does not exist!", file=sys.stderr)
        sys.exit(1)

    deobfuscate_script(script_path)

if __name__ == "__main__":
    main()

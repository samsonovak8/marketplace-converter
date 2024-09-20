import sys
import io
import shutil
import os
from main import fake_main

def run_test(file_path, output_file):
    fake_main(file_path, output_file)    
    

def main():
    test_cases = [
        ('tests/test1.txt', 'output1.txt'),
        ('tests/test2.txt', 'tests/output2.txt'),
    ]

    for input_file, output_file in test_cases:
        print(f"Running test for {input_file}...")
        run_test(input_file, output_file)
        print(f"Test for {input_file} finished. Results saved to {output_file}.")

if __name__ == "__main__":
    main()

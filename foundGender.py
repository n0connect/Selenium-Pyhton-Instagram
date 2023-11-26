import os
import re
from genderize import Genderize
from concurrent.futures import ThreadPoolExecutor
import time


def guess_gender_batch(names):
    try:
        start_time = time.time()

        # Send up to 10 names at the same time to genderize API
        batch_size = 3
        total_results = {}

        # Use set to remove repetitive names
        unique_names = list(set(names))

        for i in range(0, len(unique_names), batch_size):
            name_batch = unique_names[i:i + batch_size]
            gender_data = Genderize().get(name_batch)
            for data in gender_data:
                name = data['name']
                probability = data.get('probability', 0)
                gender = data.get('gender', None)
                if probability > 0.7:
                    total_results[name] = {'gender': gender, 'probability': probability}

        elapsed_time = time.time() - start_time
        return total_results, elapsed_time
    except Exception as e:
        print(f"Error while guessing gender: {e}")
        return {}, 0


def process_names_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        names = []
        for line in lines:
            # Remove numbers and special characters from the line, keep only the name
            name = re.sub(r'[^A-Za-z\s]', '', line).strip()
            names.append(name)

        return names
    except Exception as e:
        print(f"Error while processing names from file: {e}")
        return []


def save_to_file(names_info, gender, file_path):
    try:
        # Check existing names before opening the file
        existing_names = set()
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                existing_names = set(line.split(' --> ')[0].strip() for line in file.readlines())

        with open(file_path, 'a') as file:
            for name, info in names_info.items():
                # Do not add the name again if it already exists
                if name not in existing_names:
                    file.write(f"{name} --> Gender: {info['gender']}, Probability: {info['probability']}\n")
    except Exception as e:
        print(f"Error while saving to file: {e}")


def run_gender_guessing(file_path):
    try:
        # Check if the file path is valid
        if not os.path.isfile(file_path):
            raise ValueError("Invalid file path. Please provide a valid file path.")

        names = process_names_from_file(file_path)

        # Set the number of threads to run
        num_threads = 5

        # Split names between threads
        name_batches = [names[i:i + num_threads] for i in range(0, len(names), num_threads)]

        total_elapsed_time = 0
        final_result = {}

        # Perform name prediction in parallel
        with ThreadPoolExecutor() as executor:
            for name_batch in name_batches:
                results, elapsed_time = guess_gender_batch(name_batch)
                total_elapsed_time += elapsed_time

                # Get aggregated results
                final_result.update(results)

                # Save gendered names in appropriate files
                female_names = {name: info for name, info in results.items() if info['gender'] == 'female'}
                male_names = {name: info for name, info in results.items() if info['gender'] == 'male'}
                none_names = {name: info for name, info in results.items() if info['gender'] is None}

                save_to_file(female_names, 'female', 'female_names.txt')
                save_to_file(male_names, 'male', 'male_names.txt')
                save_to_file(none_names, 'none', 'none_names.txt')

        # Print total time and average time
        total_names = len(names)
        average_elapsed_time = total_elapsed_time / total_names if total_names > 0 else 0

        print(f"Total names: {total_names}")
        print(f"Total elapsed time: {total_elapsed_time} seconds")
        print(f"Average elapsed time per name: {average_elapsed_time} seconds")

        if len(final_result) != total_names:
            raise ValueError("Not all names have gender information.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def user_file_path():
    # Get file path from user
    file_path_input = input("Enter the file path: ")
    run_gender_guessing(file_path_input)


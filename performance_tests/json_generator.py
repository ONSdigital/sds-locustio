import json
import random
def generate_unique_identifier(existing_ids):
    while True:
        identifier = str(random.randint(10000, 99999))
        if identifier not in existing_ids:
            return identifier
def generate_unit_data():
    # Customize this function to generate whatever unit data you need
    return "Example data " + str(random.randint(1, 100))
def generate_json_data(entries_count):
    data = {
        "survey_id": "123",
        "period_id": "201801",
        "form_types": ["0001"],
        "schema_version": "v1.0.0",
        "data": []
    }
    unique_ids = set()
    for _ in range(entries_count):
        identifier = generate_unique_identifier(unique_ids)
        unique_ids.add(identifier)
        unit_data = generate_unit_data()
        data["data"].append({
            "identifier": identifier,
            "unit_data": unit_data
        })
    return data
def main():
    entries_count = int(input("Enter the number of data entries to generate: "))
    json_data = generate_json_data(entries_count)

    # Specify the output file name
    output_file_name = 'generated_data.json'
    # Write the JSON data to a file
    with open(output_file_name, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)
    print(f"Data successfully written to {output_file_name}")
    # print(json.dumps(json_data, indent=2))
if __name__ == "__main__":
    main()
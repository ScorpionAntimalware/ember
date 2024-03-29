import os
import json
import csv
from typing import List, Any

class EMBERJsonlToCSV:
    def __init__(self, features: List[str]):
        """
        EMBER dataset consists of Json Lines (.jsonl) files. Each line in the file is a JSON object.
        This class is used to extract the required features from the JSON object and generate a CSV file.

        Args:
        features (List[str]): List of features to be extracted from the JSON object.
        """
        # Add the target feature to the list of features
        # Remove the target feature from the list of features if it is already present
        # Add the target feature to the end of the list
        target = "label"
        if target in features:
            features.remove(target)

        features.append(target)

        self._features = features

    def convert(self, file_path) -> bool:
        """
        Extract the features from the JSON object and generate a CSV file.

        Args:
        file_path (str): Path to the JSONL file.

        Returns:
        bool: True if the CSV file is generated successfully, False otherwise.
        """
        if not self.check_file_path(file_path):
            print(f"File {file_path} not found.")
            return False
        
        csv_file_path = os.path.splitext(file_path)[0] + '.csv'
        print(f"CSV file will be generated at {csv_file_path}")

        # Remove the CSV file if it exists
        if os.path.exists(csv_file_path):
            print(f"The file {csv_file_path} already exists.")
            return False

        # Create a CSV file and write the header
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self._features)
            writer.writeheader()

            # Read the JSONL file and write the features to the CSV file
            with open(file_path, 'r') as file:
                i = 0
                for line in file:
                    json_data: dict = None
                    try:
                        json_data = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(e.msg())
                        os.remove(csv_file_path)
                        return False

                    data = {}

                    for feature in self._features:
                        status, value = False, None

                        if feature == "sections_mean_entropy":
                            status, value = self._get_sections_mean_entropy(json_data)
                        elif feature == "sections_min_entropy":
                            status, value = self._get_sections_min_entropy(json_data)
                        elif feature == "sections_max_entropy":
                            status, value = self._get_sections_max_entropy(json_data)
                        elif feature == "sections_mean_rawsize":
                            status, value = self._get_sections_mean_raw_size(json_data)
                        elif feature == "sections_min_rawsize":
                            status, value = self._get_sections_min_raw_size(json_data)
                        elif feature == "sections_max_rawsize":
                            status, value = self._get_sections_max_raw_size(json_data)
                        elif feature == "sections_mean_virtualsize":
                            status, value = self._get_sections_mean_virtual_size(json_data)
                        elif feature == "sections_min_virtualsize":
                            status, value = self._get_sections_min_virtual_size(json_data)
                        elif feature == "sections_max_virtualsize":
                            status, value = self._get_sections_max_virtual_size(json_data)
                        elif feature == "debug_size":
                            status, value = self._get_debug_size(json_data)
                        elif feature == "debug_rva":
                            status, value = self._get_debug_rva(json_data)
                        elif feature == "iat_rva":
                            status, value = self._get_iat_rva(json_data)
                        elif feature == "export_size":
                            status, value = self._get_export_size(json_data)
                        elif feature == "export_rva":
                            status, value = self._get_export_rva(json_data)
                        elif feature == "resource_size":
                            status, value = self._get_resource_size(json_data)
                        else:
                            status, value = self._search_and_get(json_data, feature)

                        if not status:
                            print(f"Feature '{feature}' could not be extracted.")
                            os.remove(csv_file_path)
                            return False

                        if isinstance(value, dict) or isinstance(value, list):
                            print(f"Feature '{feature}' is a complex object.")
                            os.remove(csv_file_path)
                            return False

                        data[feature] = value

                    writer.writerow(data)
                
                    i+=1
                    if i % 10000 == 0:
                        print(f"[{i}] lines processed for {file_path}")

        print(f"CSV file generated successfully at {csv_file_path}")
        return True

    def check_file_path(self, file_path) -> bool:
        """
        Check if the file exists at the given path.

        Args:
        file_path (str): Path to the file.

        Returns:
        bool: True if the file exists, False otherwise.
        """
        if not os.path.exists(file_path):
            return False
        
        return True
        
    def _search_and_get(self, json_data: dict, feature: str) -> (bool, Any):
        """
        Search recursively for the feature in the JSON object and return its value if found.

        Args:
        json_data (dict): JSON object.
        feature (str): Feature to be searched.
        default: Default value to be returned if the feature is not found.

        Returns:
        (bool, Any): True and the value of the feature if found, False and None otherwise.
        """
        for key, value in json_data.items():
            if key == feature:
                return (True, value)
            elif isinstance(value, dict):
                status, temp_value = self._search_and_get(value, feature)
                if status:
                    return (True, temp_value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        status, temp_value = self._search_and_get(item, feature)
                        if status:
                            return (True, temp_value)
                        
        return (False, None)
    

    def _get_debug_size(self, json_data: dict)-> (bool, int):
        status, datadirectories = self._search_and_get(json_data, "datadirectories")
        if not status:
            print("Datadirectories not found in the JSON object")
            return (False, None)
        
        if len(datadirectories) == 0:
            return (True, 0.0)
        
        debug_size = datadirectories[6]["size"]
        return (True, debug_size)
    
    def _get_debug_size(self, json_data: dict)-> (bool, int):
        status, datadirectories = self._search_and_get(json_data, "datadirectories")
        if not status:
            print("Datadirectories not found in the JSON object")
            return (False, None)
        
        if len(datadirectories) == 0:
            return (True, 0.0)
        
        debug_rva = datadirectories[6]["virtual_address"]
        return (True, debug_rva)
    
    def _get_debug_rva(self, json_data: dict)-> (bool, int):
        status, datadirectories = self._search_and_get(json_data, "datadirectories")
        if not status:
            print("Datadirectories not found in the JSON object")
            return (False, None)
        
        if len(datadirectories) == 0:
            return (True, 0.0)
        
        debug_rva = datadirectories[6]["virtual_address"]
        return (True, debug_rva)
    
    def _get_iat_rva(self, json_data: dict)-> (bool, int):
        status, datadirectories = self._search_and_get(json_data, "datadirectories")
        if not status:
            print("Datadirectories not found in the JSON object")
            return (False, None)
        
        if len(datadirectories) == 0:
            return (True, 0.0)
        
        iat_rva = datadirectories[12]["virtual_address"]
        return (True, iat_rva)
    
    def _get_export_size(self, json_data: dict)-> (bool, int):
        status, datadirectories = self._search_and_get(json_data, "datadirectories")
        if not status:
            print("Datadirectories not found in the JSON object")
            return (False, None)
        
        if len(datadirectories) == 0:
            return (True, 0.0)
        
        export_size = datadirectories[0]["size"]
        return (True, export_size)

    def _get_export_rva(self, json_data: dict)-> (bool, int):
        status, datadirectories = self._search_and_get(json_data, "datadirectories")
        if not status:
            print("Datadirectories not found in the JSON object")
            return (False, None)
        
        if len(datadirectories) == 0:
            return (True, 0.0)
        
        export_rva = datadirectories[0]["size"]
        return (True, export_rva)
    
    def _get_resource_size(self, json_data: dict)-> (bool, int):
        status, datadirectories = self._search_and_get(json_data, "datadirectories")
        if not status:
            print("Datadirectories not found in the JSON object")
            return (False, None)
        
        if len(datadirectories) == 0:
            return (True, 0.0)
        
        resource_size = datadirectories[2]["size"]
        return (True, resource_size)
        
    
    def _get_sections_mean_entropy(self, json_data: dict) -> (bool, float):
        """
        Calculate the mean entropy of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the mean entropy of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)

        if len(sections) == 0:
            return (True, 0.0)

        entropy_sum = 0
        feature = "entropy"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                entropy_sum += value
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, entropy_sum / len(sections))
    
    def _get_sections_min_entropy(self, json_data: dict) -> (bool, float):
        """
        Calculate the minimum entropy of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the minimum entropy of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)
        
        if len(sections) == 0:
            return (True, 0.0)

        entropy = float('inf')
        feature = "entropy"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                entropy = min(entropy, value)
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, entropy)
    
    def _get_sections_max_entropy(self, json_data: dict) -> (bool, float):
        """
        Calculate the maximum entropy of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the maximum entropy of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)
        
        if len(sections) == 0:
            return (True, 0.0)

        entropy = float('-inf')
        feature = "entropy"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                entropy = max(entropy, value)
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, entropy)
    
    def _get_sections_mean_raw_size(self, json_data: dict) -> (bool, float):
        """
        Calculate the mean raw size of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the mean raw size of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)

        if len(sections) == 0:
            return (True, 0.0)

        raw_size_sum = 0
        feature = "size"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                raw_size_sum += value
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, raw_size_sum / len(sections))
    
    def _get_sections_min_raw_size(self, json_data: dict) -> (bool, float):
        """
        Calculate the minimum raw size of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the minimum raw size of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)
        
        if len(sections) == 0:
            return (True, 0.0)

        raw_size = float('inf')
        feature = "size"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                raw_size = min(raw_size, value)
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, raw_size)
    
    def _get_sections_max_raw_size(self, json_data: dict) -> (bool, float):
        """
        Calculate the maximum raw size of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the maximum raw size of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)
        
        if len(sections) == 0:
            return (True, 0.0)

        raw_size = float('-inf')
        feature = "size"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                raw_size = max(raw_size, value)
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, raw_size)
    
    def _get_sections_mean_virtual_size(self, json_data: dict) -> (bool, float):
        """
        Calculate the mean virtual size of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the mean virtual size of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)

        if len(sections) == 0:
            return (True, 0.0)

        virtual_size_sum = 0
        feature = "vsize"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                virtual_size_sum += value
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, virtual_size_sum / len(sections))
    
    def _get_sections_min_virtual_size(self, json_data: dict) -> (bool, float):
        """
        Calculate the minimum virtual size of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the minimum virtual size of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)
        
        if len(sections) == 0:
            return (True, 0.0)

        virtual_size = float('inf')
        feature = "vsize"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                virtual_size = min(virtual_size, value)
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, virtual_size)
    
    def _get_sections_max_virtual_size(self, json_data: dict) -> (bool, float):
        """
        Calculate the maximum virtual size of the sections.

        Args:
        json_data (dict): JSON object.

        Returns:
        (bool, float): True and the maximum virtual size of the sections if successful, False and None otherwise.
        """
        status, sections = self._search_and_get(json_data, "sections")

        if not status:
            print("Sections not found in the JSON object")
            return (False, None)
        
        if len(sections) == 0:
            return (True, 0.0)

        virtual_size = float('-inf')
        feature = "vsize"

        for section in sections:
            status, value = self._search_and_get(section, feature)
            if status:
                virtual_size = max(virtual_size, value)
            else:
                print(f"{feature} not found in the section")
                return (False, None)

        return (True, virtual_size)

def main():
    # features = [
    #     "md5", 
    #     "machine", 
    #     "major_linker_version", 
    #     "minor_linker_version", 
    #     "sizeof_code", 
    #     "major_operating_system_version", 
    #     "minor_operating_system_version", 
    #     "major_image_version", 
    #     "minor_image_version", 
    #     "major_subsystem_version", 
    #     "minor_subsystem_version", 
    #     "sizeof_headers", 
    #     "subsystem", 
    #     "sizeof_heap_commit", 
    #     "sections_mean_entropy", 
    #     "sections_min_entropy", 
    #     "sections_max_entropy", 
    #     "sections_mean_rawsize", 
    #     "sections_min_rawsize", 
    #     "sections_max_rawsize", 
    #     "sections_mean_virtualsize", 
    #     "sections_min_virtualsize", 
    #     "sections_max_virtualsize"
    # ]

    features = [
        "debug_size",
        "debug_rva",
        "iat_rva",
        "export_size",
        "export_rva",
        "resource_size",
        "major_linker_version",
        "minor_linker_version",
        "major_operating_system_version",
        "minor_operating_system_version",
        "major_image_version",
        "minor_image_version",
        "exports"
    ]
    g = EMBERJsonlToCSV(features)
    if not g.convert("/path/to/data/ember2018/train_features_0.jsonl"):
        # Handle the error
        pass

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
NTBSS Save ID Parser & Extractor
Fetches and parses all save IDs from a GVAS save file
Outputs formatted ID reference list for the Save Editor
"""

import struct
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class GVASSaveParser:
    """Parse Unreal Engine GVAS save files and extract IDs"""
    
    # GVAS Magic number
    GVAS_MAGIC = 0x53564147  # "GVAS"
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data = None
        self.ids = defaultdict(list)
        self.custom_items = defaultdict(list)
        
    def read_file(self) -> bool:
        """Read the save file"""
        try:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()
            return True
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def parse_header(self) -> Tuple[bool, Dict]:
        """Parse GVAS header"""
        if len(self.data) < 16:
            return False, {}
        
        magic = struct.unpack('<I', self.data[0:4])[0]
        if magic != self.GVAS_MAGIC:
            print(f"Invalid GVAS magic: {hex(magic)}")
            return False, {}
        
        save_version = struct.unpack('<I', self.data[4:8])[0]
        package_version = struct.unpack('<I', self.data[8:12])[0]
        engine_version = struct.unpack('<I', self.data[12:16])[0]
        
        return True, {
            'save_version': save_version,
            'package_version': package_version,
            'engine_version': engine_version
        }
    
    def extract_ids(self) -> Dict[str, List[str]]:
        """Extract all ID strings from save file"""
        text_data = self.data.decode('utf-8', errors='ignore')
        
        # Regex patterns for different ID types
        patterns = {
            'Counter': r'ID_Counter_(\w+)',
            'Flag': r'ID_Flag_(\w+)',
            'Weapon': r'ID_Weapon_(\w+)',
            'Ninjutsu': r'ID_NJT_(\w+)',
            'Reward': r'ID_Reward_(\w+)',
            'Skill': r'ID_Skill_(\w+)',
            'Custom': r'ID_Custom(\w+)',
            'Parts': r'ID_Parts(\w+)',
            'Voice': r'ID_Voice_(\w+)',
            'Palette': r'ID_Pallete_(\w+)',
            'Other': r'ID_(\w+)',
        }
        
        results = defaultdict(set)
        
        for category, pattern in patterns.items():
            matches = re.findall(pattern, text_data)
            for match in matches:
                full_id = f"ID_{category}_{match}" if category != 'Counter' else f"ID_Counter_{match}"
                results[category].add(full_id)
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in results.items()}
    
    def categorize_ids(self, ids: Dict[str, List[str]]) -> Dict[str, Dict]:
        """Categorize IDs by their function"""
        categorized = {
            'currency': [],
            'scrolls': [],
            'progression': [],
            'story': [],
            'pvp': [],
            'missions': [],
            'mentors': [],
            'customization': [],
            'items': [],
            'flags': [],
            'other': []
        }
        
        # Currency
        currency_keywords = ['Money', 'SkillPoint', 'MasterPoint', 'Ryo']
        
        # Scrolls
        scroll_keywords = ['Scroll', 'CheckScroll']
        
        # Progression
        prog_keywords = ['Experience', 'PlayTime', 'UseSpecial', 'ExpBase', 'ExpScale']
        
        # Story
        story_keywords = ['Scenario', 'Lee', 'Boruto', 'Sarada', 'Ino', 'Choji', 'Sai', 'Shino', 'Hinata', 'Gaara', 'Mitsuki']
        
        # PVP
        pvp_keywords = ['PVP', 'Kill', 'Dead', 'Role']
        
        # Missions
        mission_keywords = ['Mission', 'VRMission', 'Clear', 'Rank']
        
        # Mentors
        mentor_keywords = ['Master', 'Naruto', 'Sasuke', 'Sakura', 'Kakashi', 'Tsunade', 'Jiraiya', 'Orochimaru', 'Madara', 'Minato']
        
        # Customization
        custom_keywords = ['Custom', 'Jacket', 'Pants', 'Accessory', 'FacePaint', 'Hair', 'Forehead', 'Appearance', 'Color', 'Scale', 'Voice', 'Pallete', 'Avatar', 'Nickname']
        
        for category, id_list in ids.items():
            for id_str in id_list:
                categorized_flag = False
                
                for keyword in currency_keywords:
                    if keyword in id_str:
                        categorized['currency'].append(id_str)
                        categorized_flag = True
                        break
                
                if not categorized_flag:
                    for keyword in scroll_keywords:
                        if keyword in id_str:
                            categorized['scrolls'].append(id_str)
                            categorized_flag = True
                            break
                
                if not categorized_flag:
                    for keyword in prog_keywords:
                        if keyword in id_str:
                            categorized['progression'].append(id_str)
                            categorized_flag = True
                            break
                
                if not categorized_flag:
                    for keyword in story_keywords:
                        if keyword in id_str:
                            categorized['story'].append(id_str)
                            categorized_flag = True
                            break
                
                if not categorized_flag:
                    for keyword in pvp_keywords:
                        if keyword in id_str:
                            categorized['pvp'].append(id_str)
                            categorized_flag = True
                            break
                
                if not categorized_flag:
                    for keyword in mission_keywords:
                        if keyword in id_str:
                            categorized['missions'].append(id_str)
                            categorized_flag = True
                            break
                
                if not categorized_flag:
                    for keyword in mentor_keywords:
                        if keyword in id_str:
                            categorized['mentors'].append(id_str)
                            categorized_flag = True
                            break
                
                if not categorized_flag:
                    for keyword in custom_keywords:
                        if keyword in id_str:
                            categorized['customization'].append(id_str)
                            categorized_flag = True
                            break
                
                if not categorized_flag:
                    if 'Weapon' in category or 'Ninjutsu' in category:
                        categorized['items'].append(id_str)
                        categorized_flag = True
                
                if not categorized_flag:
                    if 'Flag' in category:
                        categorized['flags'].append(id_str)
                        categorized_flag = True
                    else:
                        categorized['other'].append(id_str)
        
        return categorized
    
    def generate_report(self, categorized_ids: Dict) -> str:
        """Generate a formatted report of all IDs"""
        report = []
        report.append("=" * 80)
        report.append("NTBSS SAVE ID EXTRACTION REPORT")
        report.append("=" * 80)
        report.append(f"Save File: {self.filepath.name}\n")
        
        total_ids = 0
        
        for category, ids in categorized_ids.items():
            if ids:
                report.append(f"\n📌 {category.upper()} ({len(ids)} IDs)")
                report.append("-" * 80)
                for id_str in sorted(ids)[:20]:  # Show first 20
                    report.append(f"  {id_str}")
                if len(ids) > 20:
                    report.append(f"  ... and {len(ids) - 20} more")
                total_ids += len(ids)
        
        report.append("\n" + "=" * 80)
        report.append(f"TOTAL UNIQUE IDs FOUND: {total_ids}")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_json(self, categorized_ids: Dict, output_path: str) -> bool:
        """Export IDs as JSON"""
        try:
            with open(output_path, 'w') as f:
                json.dump(categorized_ids, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False
    
    def parse(self) -> Tuple[bool, Dict]:
        """Main parsing function"""
        if not self.read_file():
            return False, {}
        
        valid, header = self.parse_header()
        if not valid:
            print("Warning: Invalid GVAS header, attempting to extract IDs anyway...")
        
        ids = self.extract_ids()
        categorized = self.categorize_ids(ids)
        
        return True, categorized


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ntbss_id_parser.py <save_file.sav> [output.json]")
        print("\nExample:")
        print("  python ntbss_id_parser.py dumped_save.sav ntbss_ids.json")
        sys.exit(1)
    
    save_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "ntbss_ids.json"
    
    if not Path(save_file).exists():
        print(f"Error: Save file not found: {save_file}")
        sys.exit(1)
    
    print(f"Parsing save file: {save_file}")
    parser = GVASSaveParser(save_file)
    success, categorized_ids = parser.parse()
    
    if not success:
        print("Error: Failed to parse save file")
        sys.exit(1)
    
    # Print report
    report = parser.generate_report(categorized_ids)
    print("\n" + report)
    
    # Export JSON
    if parser.export_json(categorized_ids, output_file):
        print(f"\n✓ Exported IDs to: {output_file}")
    
    # Also save as text file
    text_file = output_file.replace('.json', '.txt')
    try:
        with open(text_file, 'w') as f:
            f.write(report)
        print(f"✓ Exported report to: {text_file}")
    except Exception as e:
        print(f"Warning: Could not save text report: {e}")


if __name__ == "__main__":
    main()

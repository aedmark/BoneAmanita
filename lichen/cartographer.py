import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Room:
    slug: str
    name: str
    description: str
    points_of_interest: List[str] = field(default_factory=list)
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> target_slug

class Cartographer:
    """
    Parses spatial descriptions from the LLM and maps them into graph nodes.
    Expects format:
    **[Room Name]**
    Description...
    **Points of Interest:**
    - point
    **Exits:**
    - North to [Room Name]
    """
    def __init__(self):
        self.world_map: Dict[str, Room] = {}
        self.current_room: Optional[str] = None

    def _slugify(self, text: str) -> str:
        return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')

    def parse_room(self, llm_output: str) -> Optional[Room]:
        name_match = re.search(r'\*\*\[(.*?)\]\*\*', llm_output)
        if not name_match:
            return None
            
        name = name_match.group(1).strip()
        slug = self._slugify(name)
        
        # Extract description (text between name and next bold marker)
        desc_start = name_match.end()
        next_bold = re.search(r'\*\*[^\*]+\*\*', llm_output[desc_start:])
        if next_bold:
            description = llm_output[desc_start:desc_start+next_bold.start()].strip()
        else:
            description = llm_output[desc_start:].strip()

        # Extract POIs
        pois = []
        poi_section = re.search(r'\*\*Points of Interest:\*\*(.*?)(?=\*\*|$)', llm_output, re.DOTALL | re.IGNORECASE)
        if poi_section:
            for line in poi_section.group(1).split('\n'):
                if line.strip().startswith('-'):
                    pois.append(line.replace('-', '', 1).strip())

        # Extract Exits
        exits = {}
        exits_section = re.search(r'\*\*Exits:\*\*(.*?)(?=\*\*|$)', llm_output, re.DOTALL | re.IGNORECASE)
        if exits_section:
            for line in exits_section.group(1).split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    line = line.replace('-', '', 1).strip()
                    # Expecting "North to [Target Room]" or similar
                    match = re.match(r'([A-Za-z]+)\s*(?:via.*?)?\s*to\s*(?:\[)?([^\]]+)(?:\])?', line, re.IGNORECASE)
                    if match:
                        direction = match.group(1).upper()
                        target = match.group(2).strip()
                        exits[direction] = self._slugify(target)

        room = Room(slug=slug, name=name, description=description, points_of_interest=pois, exits=exits)
        self.world_map[slug] = room
        self.current_room = slug
        return room

    def get_room(self, slug: str) -> Optional[Room]:
        return self.world_map.get(slug)

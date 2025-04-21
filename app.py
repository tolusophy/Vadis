import streamlit as st
import openai
import os
import json
import time
from typing import List, Dict, Any, Optional
import re

# Configuration and Setup
st.set_page_config(
    page_title="Vadis Media AI Film Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1E1E1E;
        border-radius: 4px;
        color: white;
        padding: 10px 16px;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3366FF !important;
    }
    h1, h2, h3 {
        color: #3366FF;
    }
    .project-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .agent-message {
        background-color: #2C2C2C;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'api_key_configured' not in st.session_state:
    st.session_state.api_key_configured = False
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = "concept"
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Agent System - Using OpenAI's GPT models
class Agent:
    def __init__(self, api_key, model="gpt-4o", temperature=0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_response(self, prompt, system_message, conversation_history=None):
        try:
            messages = [{"role": "system", "content": system_message}]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class FilmConceptAgent(Agent):
    def __init__(self, api_key, model="gpt-4o"):
        super().__init__(api_key, model, temperature=0.8)
        self.system_message = """
        You are an expert film concept creator with decades of experience in the film industry.
        Your task is to generate innovative and compelling film concepts based on user inputs.
        Consider current trends, audience preferences, and provide a range of options that vary in tone, style, and approach.
        Each concept should include a catchy title, a brief logline, and a short synopsis that outlines the main plot.
        Your concepts should be marketable, unique, and have strong potential for both critical acclaim and commercial success.
        """
    
    def generate_concepts(self, user_inputs, num_concepts=3):
        prompt = f"""
        Generate {num_concepts} distinct film concepts based on the following parameters:
        
        Genre: {user_inputs.get('genre', 'Not specified')}
        Target Rating: {user_inputs.get('rating', 'Not specified')}
        Key Themes: {user_inputs.get('themes', 'Not specified')}
        Target Audience: {user_inputs.get('audience', 'Not specified')}
        Additional Notes: {user_inputs.get('additional_notes', 'None')}
        
        For each concept, provide:
        1. Title
        2. Logline (one sentence)
        3. Synopsis (2-3 paragraphs)
        4. Key selling points (what makes this marketable)
        5. Potential audience appeal
        
        Format each concept clearly and label them as CONCEPT 1, CONCEPT 2, etc.
        """
        return self.generate_response(prompt, self.system_message)

class ScriptAgent(Agent):
    def __init__(self, api_key, model="gpt-4o"):
        super().__init__(api_key, model, temperature=0.7)
        self.system_message = """
        You are an experienced screenwriter with expertise in creating professional-quality film scripts.
        Your writing adheres to industry-standard screenplay format. 
        You create compelling dialogue, clear action descriptions, and properly formatted scene headings.
        Your scripts maintain consistent tone, voice, and pacing appropriate to the genre and project requirements.
        """
    
    def generate_treatment(self, concept, additional_details=None):
        prompt = f"""
        Create a detailed film treatment based on the following concept:
        
        {concept}
        
        Additional details to incorporate: {additional_details if additional_details else 'None provided'}
        
        The treatment should include:
        1. An expanded synopsis (5-7 paragraphs)
        2. A clear three-act structure
        3. Major plot points and turning points
        4. Character development arcs for the main characters
        5. Thematic elements to be explored
        
        This treatment will serve as the foundation for the full script development.
        """
        return self.generate_response(prompt, self.system_message)
    
    def generate_script_outline(self, treatment, num_scenes=12):
        prompt = f"""
        Based on the following treatment, create a detailed script outline with approximately {num_scenes} key scenes:
        
        {treatment}
        
        For each scene, provide:
        1. Scene heading (INT/EXT, LOCATION, TIME)
        2. Brief description of the setting
        3. Characters present
        4. Summary of the action (what happens)
        5. Purpose of the scene in advancing the plot or character development
        
        Order the scenes chronologically and ensure they follow a cohesive narrative arc.
        """
        return self.generate_response(prompt, self.system_message)
    
    def generate_scene(self, scene_description, characters, previous_scenes=None):
        context = f"Previous scenes: {previous_scenes}\n\n" if previous_scenes else ""
        
        prompt = f"""
        {context}
        Write a professional screenplay scene based on the following description:
        
        Scene description: {scene_description}
        Characters present: {characters}
        
        Use proper screenplay format including:
        - Scene heading
        - Action descriptions
        - Character names
        - Dialogue
        - Parentheticals where appropriate
        - Transitions where appropriate
        
        Keep the scene concise but effective, with natural dialogue and clear action descriptions.
        """
        return self.generate_response(prompt, self.system_message)

class CastingAgent(Agent):
    def __init__(self, api_key, model="gpt-4o"):
        super().__init__(api_key, model, temperature=0.7)
        self.system_message = """
        You are an expert casting director with extensive knowledge of actors across Hollywood and international cinema.
        Your specialty is matching character descriptions with ideal actors who would bring authenticity, star power, and the right qualities to a role.
        You know actors' past performances, physical characteristics, acting styles, current popularity, and typical casting rates.
        Make casting suggestions that balance artistic integrity with commercial viability, considering both established stars and promising new talent.
        """
    
    def suggest_cast(self, characters_descriptions, budget_level="medium", exclude_actors=None):
        exclude_str = ", ".join(exclude_actors) if exclude_actors else "None"
        
        prompt = f"""
        Suggest ideal casting choices for the following characters in a {budget_level}-budget film:
        
        {characters_descriptions}
        
        Actors to exclude from consideration: {exclude_str}
        
        For each character, provide:
        1. Three potential actors who would excel in the role (prioritize actors who are currently active)
        2. Brief explanation of why each actor would be suitable
        3. Notable similar roles they've played that demonstrate their fit
        4. Any potential scheduling, budget, or casting challenges to consider
        
        Provide a mix of established stars and rising talent as appropriate for the budget level.
        """
        return self.generate_response(prompt, self.system_message)

class LocationAgent(Agent):
    def __init__(self, api_key, model="gpt-4o"):
        super().__init__(api_key, model, temperature=0.6)
        self.system_message = """
        You are an experienced film location scout with global expertise in finding perfect filming locations.
        You understand both the creative aspects (visual style, atmosphere, setting authenticity) and practical considerations (permits, costs, facilities, crew access, weather patterns).
        You know which countries and regions offer film production incentives and tax benefits.
        You provide specific, actionable location recommendations that balance creative vision with logistical reality.
        """
    
    def suggest_locations(self, script_elements, budget_level="medium", special_requirements=None):
        requirements = special_requirements if special_requirements else "None specified"
        
        prompt = f"""
        Recommend optimal filming locations for a {budget_level}-budget film with the following elements:
        
        {script_elements}
        
        Special requirements: {requirements}
        
        For each major setting in the script, suggest:
        1. Primary location recommendation (specific city/region/country)
        2. Alternative location options that could work as substitutes
        3. Key benefits of each location (visual style, authenticity, production incentives)
        4. Practical considerations (weather seasons, permit requirements, logistical challenges)
        5. Estimated cost impact (high/medium/low) relative to the budget level
        
        Focus on locations that offer the best combination of creative fit, production value, and financial incentives.
        """
        return self.generate_response(prompt, self.system_message)

class ProductPlacementAgent(Agent):
    def __init__(self, api_key, model="gpt-4o"):
        super().__init__(api_key, model, temperature=0.7)
        self.system_message = """
        You are a product placement and brand integration specialist with expertise in seamlessly incorporating brands into film content.
        You understand how to identify natural placement opportunities that don't feel forced but provide value to brands.
        You know which brands align with different film genres, character types, and target audiences.
        You can suggest both obvious and subtle placement opportunities, from featured products to background elements.
        You understand the financial considerations of different placement types and their potential value.
        """
    
    def suggest_placements(self, script_elements, target_audience, genre):
        prompt = f"""
        Identify natural product placement opportunities for a film with the following elements:
        
        Script elements: {script_elements}
        Target audience: {target_audience}
        Genre: {genre}
        
        For each placement opportunity, provide:
        1. The scene or context where the placement would occur
        2. Specific brands that would be ideal fits (suggest 2-3 options per opportunity)
        3. How the product would be integrated (background, mentioned in dialogue, actively used by character, etc.)
        4. Why this placement feels natural rather than forced
        5. The potential value tier of the placement (high/medium/low)
        
        Suggest at least 5 different placement opportunities across various categories (e.g., technology, food/beverage, automotive, fashion, etc.).
        Focus on placements that would feel authentic to the story and characters.
        """
        return self.generate_response(prompt, self.system_message)

class MarketingAgent(Agent):
    def __init__(self, api_key, model="gpt-4o"):
        super().__init__(api_key, model, temperature=0.8)
        self.system_message = """
        You are an expert film marketing strategist who specializes in creating compelling promotional materials and strategies.
        You know how to position films to appeal to their target audiences while highlighting their unique selling points.
        You understand both traditional marketing channels and digital/social media strategies.
        You can create taglines, poster concepts, and trailer strategies that capture the essence of a film.
        Your goal is to maximize audience interest and box office potential through effective marketing.
        """
    
    def generate_marketing_assets(self, film_details, target_audience):
        prompt = f"""
        Create key marketing assets for the following film:
        
        Film details: {film_details}
        Target audience: {target_audience}
        
        Provide:
        
        1. Three potential taglines that capture the film's essence
        2. A detailed poster concept description (visual elements, style, composition)
        3. A trailer strategy (what scenes/moments to highlight, tone, music suggestions)
        4. Three key selling points to emphasize in marketing materials
        5. Social media strategy (platform focus, content types, hashtag suggestions)
        
        Ensure all elements align with the target audience preferences and highlight what makes this film unique and appealing.
        """
        return self.generate_response(prompt, self.system_message)

# Multi-Agent System Coordinator
class FilmAISystem:
    def __init__(self, api_key):
        self.api_key = api_key
        self.concept_agent = FilmConceptAgent(api_key)
        self.script_agent = ScriptAgent(api_key)
        self.casting_agent = CastingAgent(api_key)
        self.location_agent = LocationAgent(api_key)
        self.placement_agent = ProductPlacementAgent(api_key)
        self.marketing_agent = MarketingAgent(api_key)
    
    def generate_film_concept(self, user_inputs):
        return self.concept_agent.generate_concepts(user_inputs)
    
    def develop_treatment(self, concept, additional_details=None):
        return self.script_agent.generate_treatment(concept, additional_details)
    
    def create_script_outline(self, treatment):
        return self.script_agent.generate_script_outline(treatment)
    
    def write_scene(self, scene_description, characters, previous_scenes=None):
        return self.script_agent.generate_scene(scene_description, characters, previous_scenes)
    
    def suggest_cast(self, character_descriptions, budget_level="medium"):
        return self.casting_agent.suggest_cast(character_descriptions, budget_level)
    
    def suggest_locations(self, script_elements, budget_level="medium", special_requirements=None):
        return self.location_agent.suggest_locations(script_elements, budget_level, special_requirements)
    
    def suggest_product_placements(self, script_elements, target_audience, genre):
        return self.placement_agent.suggest_placements(script_elements, target_audience, genre)
    
    def create_marketing_assets(self, film_details, target_audience):
        return self.marketing_agent.generate_marketing_assets(film_details, target_audience)

# Project Management Functions
def create_new_project(title, genre, concept):
    project = {
        "id": len(st.session_state.projects) + 1,
        "title": title,
        "genre": genre,
        "concept": concept,
        "treatment": None,
        "script_outline": None,
        "cast_suggestions": None,
        "location_suggestions": None,
        "product_placements": None,
        "marketing_assets": None,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.projects.append(project)
    return project

def update_project(project_id, key, value):
    for project in st.session_state.projects:
        if project["id"] == project_id:
            project[key] = value
            project["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            break

def get_project(project_id):
    for project in st.session_state.projects:
        if project["id"] == project_id:
            return project
    return None

# UI Components
def display_header():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://placekitten.com/200/100", width=150)  # Placeholder for Vadis Media logo
    with col2:
        st.title("Vadis Media AI Film Platform")
        st.subheader("Create, Develop, and Market Film Projects with AI")

def display_api_key_input():
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Enter OpenAI API Key", type="password")
        if st.button("Save API Key"):
            if api_key.startswith("sk-") and len(api_key) > 20:
                st.session_state.api_key = api_key
                st.session_state.api_key_configured = True
                st.success("API Key configured successfully!")
            else:
                st.error("Invalid API Key format. Please check and try again.")

def display_project_selector():
    with st.sidebar:
        st.header("Projects")
        if len(st.session_state.projects) > 0:
            project_titles = [f"{p['id']}: {p['title']}" for p in st.session_state.projects]
            selected_project = st.selectbox("Select Project", ["Create New Project"] + project_titles)
            
            if selected_project != "Create New Project":
                project_id = int(selected_project.split(":")[0])
                st.session_state.current_project = get_project(project_id)
                if st.button("View Selected Project"):
                    st.session_state.current_step = "overview"
        
        if st.button("Create New Project"):
            st.session_state.current_project = None
            st.session_state.current_step = "concept"

def display_project_concept_creator():
    st.header("Create New Film Project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_title = st.text_input("Working Title", placeholder="Enter a working title for your project")
        
        genre_options = [
            "Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", 
            "Fantasy", "Historical", "Horror", "Romance", "Science Fiction", "Thriller"
        ]
        genre = st.selectbox("Primary Genre", genre_options)
        
        rating_options = ["G", "PG", "PG-13", "R", "NC-17"]
        rating = st.selectbox("Target Rating", rating_options)
        
    with col2:
        themes = st.text_input("Key Themes", placeholder="e.g., redemption, family, survival")
        audience = st.text_input("Target Audience", placeholder="e.g., 18-35 male, family, etc.")
        additional_notes = st.text_area("Additional Notes", placeholder="Any specific elements or ideas you want to include")
    
    user_inputs = {
        "genre": genre,
        "rating": rating,
        "themes": themes,
        "audience": audience,
        "additional_notes": additional_notes
    }
    
    if st.button("Generate Concepts"):
        with st.spinner("Generating film concepts..."):
            if not hasattr(st.session_state, 'api_key'):
                st.error("Please configure your OpenAI API key first.")
                return
            
            system = FilmAISystem(st.session_state.api_key)
            concepts = system.generate_film_concept(user_inputs)
            
            st.session_state.generated_concepts = concepts
            st.session_state.conversation_history.append({
                "role": "agent",
                "content": concepts,
                "agent_type": "concept_agent"
            })
    
    if 'generated_concepts' in st.session_state:
        st.subheader("Generated Concepts")
        st.markdown(st.session_state.generated_concepts)
        
        # Extract concept titles using regex
        concept_pattern = r"CONCEPT \d+:?\s*([^\n]+)"
        concept_titles = re.findall(concept_pattern, st.session_state.generated_concepts)
        
        if concept_titles:
            selected_concept = st.selectbox("Select a concept to develop", concept_titles)
            
            if st.button("Develop Selected Concept"):
                # Find the full concept text
                selected_index = concept_titles.index(selected_concept)
                concept_start_pattern = f"CONCEPT {selected_index+1}"
                
                concept_starts = [m.start() for m in re.finditer(f"CONCEPT {selected_index+1}", st.session_state.generated_concepts)]
                if concept_starts:
                    start_pos = concept_starts[0]
                    
                    # Find the start of the next concept or use the end of string
                    next_concept_pattern = f"CONCEPT {selected_index+2}"
                    next_starts = [m.start() for m in re.finditer(next_concept_pattern, st.session_state.generated_concepts)]
                    
                    if next_starts:
                        end_pos = next_starts[0]
                    else:
                        end_pos = len(st.session_state.generated_concepts)
                    
                    full_concept = st.session_state.generated_concepts[start_pos:end_pos].strip()
                    
                    # Create new project
                    new_project = create_new_project(selected_concept, genre, full_concept)
                    st.session_state.current_project = new_project
                    st.session_state.current_step = "treatment"
                    st.experimental_rerun()

def display_project_treatment_developer():
    project = st.session_state.current_project
    
    st.header(f"Develop Treatment: {project['title']}")
    
    st.subheader("Selected Concept")
    st.markdown(project["concept"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        additional_details = st.text_area("Additional Treatment Notes", 
                                        placeholder="Any specific elements you want included in the treatment",
                                        height=150)
    
    with col2:
        st.markdown("#### Treatment Development")
        st.markdown("The treatment will expand the concept into a detailed outline of the film, including:")
        st.markdown("- Extended synopsis")
        st.markdown("- Three-act structure")
        st.markdown("- Character arcs")
        st.markdown("- Thematic elements")
    
    if st.button("Generate Treatment"):
        with st.spinner("Developing treatment..."):
            if not hasattr(st.session_state, 'api_key'):
                st.error("Please configure your OpenAI API key first.")
                return
            
            system = FilmAISystem(st.session_state.api_key)
            treatment = system.develop_treatment(project["concept"], additional_details)
            
            update_project(project["id"], "treatment", treatment)
            st.session_state.conversation_history.append({
                "role": "agent",
                "content": treatment,
                "agent_type": "script_agent"
            })
            
            st.experimental_rerun()
    
    if project["treatment"]:
        st.subheader("Generated Treatment")
        st.markdown(project["treatment"])
        
        if st.button("Proceed to Script Outline"):
            st.session_state.current_step = "script_outline"
            st.experimental_rerun()

def display_script_outline_developer():
    project = st.session_state.current_project
    
    st.header(f"Develop Script Outline: {project['title']}")
    
    if not project["treatment"]:
        st.error("Please generate a treatment first.")
        if st.button("Go Back to Treatment"):
            st.session_state.current_step = "treatment"
            st.experimental_rerun()
        return
    
    st.subheader("Treatment Summary")
    # Show just the first 500 characters of the treatment
    st.markdown(project["treatment"][:500] + "...")
    with st.expander("View Full Treatment"):
        st.markdown(project["treatment"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_scenes = st.slider("Number of Key Scenes", min_value=8, max_value=30, value=12)
    
    with col2:
        st.markdown("#### Script Outline Development")
        st.markdown("The script outline will structure the film into specific scenes, including:")
        st.markdown("- Scene headings and settings")
        st.markdown("- Characters present")
        st.markdown("- Action summaries")
        st.markdown("- Narrative purpose of each scene")
    
    if st.button("Generate Script Outline"):
        with st.spinner("Developing script outline..."):
            if not hasattr(st.session_state, 'api_key'):
                st.error("Please configure your OpenAI API key first.")
                return
            
            system = FilmAISystem(st.session_state.api_key)
            script_outline = system.create_script_outline(project["treatment"], num_scenes)
            
            update_project(project["id"], "script_outline", script_outline)
            st.session_state.conversation_history.append({
                "role": "agent",
                "content": script_outline,
                "agent_type": "script_agent"
            })
            
            st.experimental_rerun()
    
    if project["script_outline"]:
        st.subheader("Generated Script Outline")
        st.markdown(project["script_outline"])
        
        if st.button("Proceed to Casting"):
            st.session_state.current_step = "casting"
            st.experimental_rerun()

def display_casting_developer():
    project = st.session_state.current_project
    
    st.header(f"Casting Suggestions: {project['title']}")
    
    if not project["script_outline"]:
        st.error("Please generate a script outline first.")
        if st.button("Go Back to Script Outline"):
            st.session_state.current_step = "script_outline"
            st.experimental_rerun()
        return
    
    st.subheader("Character Analysis")
    
    character_descriptions = st.text_area("Character Descriptions", 
                                        placeholder="List each main character with a brief description of their traits, age, and background",
                                        height=200)
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget_options = ["Low", "Medium", "High", "Blockbuster"]
        budget_level = st.selectbox("Budget Level", budget_options)
    
    with col2:
        excluded_actors = st.text_input("Actors to Exclude", 
                                      placeholder="List any actors to exclude, separated by commas")
    
    if st.button("Generate Casting Suggestions"):
        with st.spinner("Developing casting suggestions..."):
            if not hasattr(st.session_state, 'api_key'):
                st.error("Please configure your OpenAI API key first.")
                return
            
            system = FilmAISystem(st.session_state.api_key)
            
            exclude_list = [actor.strip() for actor in excluded_actors.split(",")] if excluded_actors else None
            casting = system.suggest_cast(character_descriptions, budget_level.lower(), exclude_list)
            
            update_project(project["id"], "cast_suggestions", casting)
            st.session_state.conversation_history.append({
                "role": "agent",
                "content": casting,
                "agent_type": "casting_agent"
            })
            
            st.experimental_rerun()
    
    if project["cast_suggestions"]:
        st.subheader("Generated Casting Suggestions")
        st.markdown(project["cast_suggestions"])
        
        if st.button("Proceed to Locations"):
            st.session_state.current_step = "locations"
            st.experimental_rerun()

def display_locations_developer():
    project = st.session_state.current_project
    
    st.header(f"Location Suggestions: {project['title']}")
    
    if not project["script_outline"]:
        st.error("Please generate a script outline first.")
        if st.button("Go Back to Script Outline"):
            st.session_state.current_step = "script_outline"
            st.experimental_rerun()
        return
    
    st.subheader("Location Requirements")
    
    script_elements = st.text_area("Key Setting Elements", 
                                 placeholder="List the main settings and environments needed in the film",
                                 height=150)
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget_options = ["Low", "Medium", "High", "Blockbuster"]
        budget_level = st.selectbox("Budget Level", budget_options)
    
    with col2:
        special_requirements = st.text_input("Special Requirements", 
                                          placeholder="Any specific needs, e.g., snow, desert, accessibility")
    
    if st.button("Generate Location Suggestions"):
        with st.spinner("Developing location suggestions..."):
            if not hasattr(st.session_state, 'api_key'):
                st.error("Please configure your OpenAI API key first.")
                return
            
            system = FilmAISystem(st.session_state.api_key)
            locations = system.suggest_locations(script_elements, budget_level.lower(), special_requirements)
            
            update_project(project["id"], "location_suggestions", locations)
            st.session_state.conversation_history.append({
                "role": "agent",
                "content": locations,
                "agent_type": "location_agent"
            })
            
            st.experimental_rerun()
    
    if project["location_suggestions"]:
        st.subheader("Generated Location Suggestions")
        st.markdown(project["location_suggestions"])
        
        if st.button("Proceed to Product Placements"):
            st.session_state.current_step = "product_placements"
            st.experimental_rerun()

def display_product_placements_developer():
    project = st.session_state.current_project
    
    st.header(f"Product Placement Opportunities: {project['title']}")
    
    if not project["script_outline"]:
        st.error("Please generate a script outline first.")
        if st.button("Go Back to Script Outline"):
            st.session_state.current_step = "script_outline"
            st.experimental_rerun()
        return
    
    st.subheader("Product Placement Analysis")
    
    script_elements = st.text_area("Key Scene Elements", 
                                 placeholder="Describe the main scenes where product placements could fit naturally",
                                 height=150)
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_audience = st.text_input("Target Audience", 
                                     placeholder="e.g., 18-35 male, family, etc.")
    
    with col2:
        genre_options = [
            "Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", 
            "Fantasy", "Historical", "Horror", "Romance", "Science Fiction", "Thriller"
        ]
        genre = st.selectbox("Film Genre", genre_options)
    
    if st.button("Generate Product Placement Opportunities"):
        with st.spinner("Identifying product placement opportunities..."):
            if not hasattr(st.session_state, 'api_key'):
                st.error("Please configure your OpenAI API key first.")
                return
            
            system = FilmAISystem(st.session_state.api_key)
            placements = system.suggest_product_placements(script_elements, target_audience, genre)
            
            update_project(project["id"], "product_placements", placements)
            st.session_state.conversation_history.append({
                "role": "agent",
                "content": placements,
                "agent_type": "placement_agent"
            })
            
            st.experimental_rerun()
    
    if project["product_placements"]:
        st.subheader("Generated Product Placement Opportunities")
        st.markdown(project["product_placements"])
        
        if st.button("Proceed to Marketing"):
            st.session_state.current_step = "marketing"
            st.experimental_rerun()

def display_marketing_developer():
    project = st.session_state.current_project
    
    st.header(f"Marketing Assets: {project['title']}")
    
    if not project["treatment"]:
        st.error("Please generate a treatment first.")
        if st.button("Go Back to Treatment"):
            st.session_state.current_step = "treatment"
            st.experimental_rerun()
        return
    
    st.subheader("Marketing Strategy Development")
    
    # Compile film details from the project
    film_summary = f"""Title: {project['title']}
Genre: {project['genre']}
Concept: {project['concept'][:500]}..."""

    st.text_area("Film Summary", film_summary, height=150, disabled=True)
    
    target_audience = st.text_input("Target Audience", 
                                 placeholder="e.g., 18-35 male, family, etc.")
    
    if st.button("Generate Marketing Assets"):
        with st.spinner("Developing marketing assets..."):
            if not hasattr(st.session_state, 'api_key'):
                st.error("Please configure your OpenAI API key first.")
                return
            
            system = FilmAISystem(st.session_state.api_key)
            marketing = system.create_marketing_assets(film_summary, target_audience)
            
            update_project(project["id"], "marketing_assets", marketing)
            st.session_state.conversation_history.append({
                "role": "agent",
                "content": marketing,
                "agent_type": "marketing_agent"
            })
            
            st.experimental_rerun()
    
    if project["marketing_assets"]:
        st.subheader("Generated Marketing Assets")
        st.markdown(project["marketing_assets"])
        
        if st.button("View Complete Project"):
            st.session_state.current_step = "overview"
            st.experimental_rerun()

def display_project_overview():
    project = st.session_state.current_project
    
    st.header(f"Project Overview: {project['title']}")
    
    tabs = st.tabs(["Summary", "Treatment", "Script Outline", "Cast", "Locations", "Product Placements", "Marketing"])
    
    with tabs[0]:
        st.subheader("Project Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {project['title']}")
            st.markdown(f"**Genre:** {project['genre']}")
            st.markdown(f"**Created:** {project['created_at']}")
            st.markdown(f"**Last Updated:** {project['updated_at']}")
        
        with col2:
            # Calculate completion status
            completed_elements = sum(1 for key in ['concept', 'treatment', 'script_outline', 
                                                 'cast_suggestions', 'location_suggestions', 
                                                 'product_placements', 'marketing_assets'] 
                                  if project[key])
            completion_percentage = (completed_elements / 7) * 100
            
            st.metric("Completion Status", f"{int(completion_percentage)}%")
            
            # Next steps
            st.subheader("Next Steps")
            next_step = None
            if not project["treatment"]:
                next_step = ("Treatment", "treatment")
            elif not project["script_outline"]:
                next_step = ("Script Outline", "script_outline")
            elif not project["cast_suggestions"]:
                next_step = ("Casting", "casting")
            elif not project["location_suggestions"]:
                next_step = ("Locations", "locations")
            elif not project["product_placements"]:
                next_step = ("Product Placements", "product_placements")
            elif not project["marketing_assets"]:
                next_step = ("Marketing", "marketing")
            
            if next_step:
                st.markdown(f"Continue to: **{next_step[0]}**")
                if st.button(f"Go to {next_step[0]}"):
                    st.session_state.current_step = next_step[1]
                    st.experimental_rerun()
            else:
                st.success("Project development complete!")
                
        st.subheader("Concept")
        st.markdown(project["concept"])
    
    with tabs[1]:
        st.subheader("Treatment")
        if project["treatment"]:
            st.markdown(project["treatment"])
        else:
            st.info("Treatment not yet generated")
            if st.button("Generate Treatment"):
                st.session_state.current_step = "treatment"
                st.experimental_rerun()
    
    with tabs[2]:
        st.subheader("Script Outline")
        if project["script_outline"]:
            st.markdown(project["script_outline"])
        else:
            st.info("Script outline not yet generated")
            if st.button("Generate Script Outline"):
                st.session_state.current_step = "script_outline"
                st.experimental_rerun()
    
    with tabs[3]:
        st.subheader("Cast Suggestions")
        if project["cast_suggestions"]:
            st.markdown(project["cast_suggestions"])
        else:
            st.info("Cast suggestions not yet generated")
            if st.button("Generate Cast Suggestions"):
                st.session_state.current_step = "casting"
                st.experimental_rerun()
    
    with tabs[4]:
        st.subheader("Location Suggestions")
        if project["location_suggestions"]:
            st.markdown(project["location_suggestions"])
        else:
            st.info("Location suggestions not yet generated")
            if st.button("Generate Location Suggestions"):
                st.session_state.current_step = "locations"
                st.experimental_rerun()
    
    with tabs[5]:
        st.subheader("Product Placement Opportunities")
        if project["product_placements"]:
            st.markdown(project["product_placements"])
        else:
            st.info("Product placement opportunities not yet generated")
            if st.button("Generate Product Placement Opportunities"):
                st.session_state.current_step = "product_placements"
                st.experimental_rerun()
    
    with tabs[6]:
        st.subheader("Marketing Assets")
        if project["marketing_assets"]:
            st.markdown(project["marketing_assets"])
        else:
            st.info("Marketing assets not yet generated")
            if st.button("Generate Marketing Assets"):
                st.session_state.current_step = "marketing"
                st.experimental_rerun()

def display_conversation_history():
    if st.session_state.conversation_history:
        st.header("AI Agent Activity")
        
        for message in st.session_state.conversation_history[-3:]:  # Show only the last 3 entries
            agent_type = message.get("agent_type", "system")
            agent_name_map = {
                "concept_agent": "Film Concept Agent",
                "script_agent": "Script Development Agent",
                "casting_agent": "Casting Agent",
                "location_agent": "Location Scout Agent",
                "placement_agent": "Product Placement Agent",
                "marketing_agent": "Marketing Agent",
                "system": "System"
            }
            
            agent_name = agent_name_map.get(agent_type, agent_type)
            
            with st.expander(f"{agent_name} Output"):
                st.markdown(message["content"])

# Main Application
def main():
    display_header()
    
    # API Key Configuration
    if not st.session_state.api_key_configured:
        display_api_key_input()
        st.warning("Please configure your OpenAI API key to continue.")
        return
    
    # Project Selector in Sidebar
    display_project_selector()
    
    # Main Content Area
    if st.session_state.current_step == "concept" and not st.session_state.current_project:
        display_project_concept_creator()
    elif st.session_state.current_step == "treatment" and st.session_state.current_project:
        display_project_treatment_developer()
    elif st.session_state.current_step == "script_outline" and st.session_state.current_project:
        display_script_outline_developer()
    elif st.session_state.current_step == "casting" and st.session_state.current_project:
        display_casting_developer()
    elif st.session_state.current_step == "locations" and st.session_state.current_project:
        display_locations_developer()
    elif st.session_state.current_step == "product_placements" and st.session_state.current_project:
        display_product_placements_developer()
    elif st.session_state.current_step == "marketing" and st.session_state.current_project:
        display_marketing_developer()
    elif st.session_state.current_step == "overview" and st.session_state.current_project:
        display_project_overview()
    
    # Conversation History at the Bottom
    display_conversation_history()

    # Footer
    st.markdown("---")
    st.markdown("**Vadis Media AI Film Platform** - MVP Demo - Festival de Cannes 2025")

if __name__ == "__main__":
    main()
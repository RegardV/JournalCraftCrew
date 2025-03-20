from crewai import Agent
from crewai.tools import BaseTool
import json
import os
from fpdf import FPDF
from config.settings import JSON_SUBDIR, PDF_SUBDIR, MEDIA_SUBDIR
from utils import log_debug

class PDFCreatorTool(BaseTool):
    name: str = "create_pdf"
    description: str = "Generate professionally formatted PDF documents from course content"

    def _run(self, content: dict, output_path: str, use_media: bool = False, media_dir: str = None, epub_kdp: bool = False):
        """Generate a PDF with specified layout for journaling content."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add Unicode fonts (DejaVuSans for regular and bold)
        regular_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        bold_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        # Load regular font (required)
        if os.path.exists(regular_font_path):
            pdf.add_font("DejaVu", "", regular_font_path, uni=True)
        else:
            log_debug(f"Regular font {regular_font_path} not found, falling back to Arial")
            pdf.set_font("Arial", size=12)  # Fallback to built-in Arial
        
        # Load bold font (optional, with fallback)
        if os.path.exists(bold_font_path):
            pdf.add_font("DejaVu", "B", bold_font_path, uni=True)
            bold_available = True
        else:
            log_debug(f"Bold font {bold_font_path} not found, using regular DejaVu for bold text")
            bold_available = False
        
        # Set default font
        pdf.set_font("DejaVu", size=12)
        
        # Page 1: Blank
        pdf.add_page()

        # Page 2: Quote (from intro_spread.left.quote)
        pdf.add_page()
        pdf.set_font("DejaVu", "B" if bold_available else "", 14)  # Bold if available
        pdf.cell(0, 10, "Welcome", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        if "intro_spread" in content and "left" in content["intro_spread"] and "quote" in content["intro_spread"]["left"]:
            pdf.ln(50)  # Move to approximate middle
            pdf.multi_cell(0, 10, content["intro_spread"]["left"]["quote"], align="C")

        # Page 3: Introduction (from intro_spread.right.writeup)
        pdf.add_page()
        pdf.set_font("DejaVu", "B" if bold_available else "", 14)
        pdf.cell(0, 10, "Introduction", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        if "intro_spread" in content and "right" in content["intro_spread"] and "writeup" in content["intro_spread"]["right"]:
            pdf.ln(50)
            pdf.multi_cell(0, 10, content["intro_spread"]["right"]["writeup"], align="C")

        # Page 4: Commitment
        pdf.add_page()
        pdf.set_font("DejaVu", "B" if bold_available else "", 14)
        pdf.cell(0, 10, "My Commitment", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        if "commitment_page" in content and "writeup" in content["commitment_page"]:
            pdf.ln(50)
            pdf.multi_cell(0, 10, content["commitment_page"]["writeup"], align="C")
            pdf.set_y(-30)  # Near bottom
            pdf.cell(0, 10, "Signature: ______________________________", ln=True, align="C")

        # Day Pages
        if "days" in content and not epub_kdp:
            for day in content["days"]:
                # First page: Day, Image, Pre-writeup, Bottom Image
                pdf.add_page()
                pdf.set_font("DejaVu", "B" if bold_available else "", 14)
                pdf.cell(0, 10, f"Day {day['day']}", ln=True, align="C")
                pdf.set_font("DejaVu", size=12)
                
                # Image placeholder (top center)
                image_path = os.path.join(media_dir, f"{day['image_full_page']}.png") if use_media and media_dir else None
                if use_media and media_dir and os.path.exists(image_path) and image_path.endswith('.png'):
                    pdf.image(image_path, x=(pdf.w - 100) / 2, y=20, w=100)
                    pdf.ln(110)  # Move below image
                else:
                    pdf.ln(10)
                    pdf.cell(0, 10, f"[Image: {day['image_full_page']}]", ln=True, align="C")
                    pdf.ln(10)
                
                # Pre-writeup
                pdf.multi_cell(0, 10, day["pre_writeup"], align="C")
                
                # Bottom image (branding)
                bottom_image_path = os.path.join(media_dir, f"{day['image_bottom']}.png") if use_media and media_dir else None
                pdf.set_y(-30)
                # Note: Fixed typo 'custom_image_path' to 'bottom_image_path'
                if use_media and media_dir and os.path.exists(bottom_image_path) and bottom_image_path.endswith('.png'):
                    pdf.image(bottom_image_path, x=(pdf.w - 100) / 2, w=100)
                else:
                    pdf.cell(0, 10, f"[Image: {day['image_bottom']}]", ln=True, align="C")

                # Second page: Prompt and Lines
                pdf.add_page()
                pdf.set_font("DejaVu", "B" if bold_available else "", 14)
                pdf.cell(0, 10, "Prompt", ln=True, align="C")
                pdf.set_font("DejaVu", size=12)
                pdf.ln(10)
                pdf.multi_cell(0, 10, day["prompt"], align="C")
                pdf.ln(10)
                y_start = pdf.get_y()
                while y_start < pdf.h - 20:  # Full page minus margins
                    pdf.line(10, y_start, pdf.w - 10, y_start)  # Full-width thin line
                    y_start += 5
                pdf.set_line_width(0.1)  # Very thin lines

        # Certificate Page
        if "certificate" in content:
            pdf.add_page()
            pdf.set_font("DejaVu", "B" if bold_available else "", 14)
            pdf.cell(0, 10, "Congratulations", ln=True, align="C")
            pdf.set_font("DejaVu", size=12)
            pdf.ln(50)
            if "summary" in content["certificate"]:
                pdf.multi_cell(0, 10, content["certificate"]["summary"], align="C")
            if "text" in content["certificate"]:
                pdf.ln(10)
                pdf.multi_cell(0, 10, content["certificate"]["text"], align="C")

        pdf.output(output_path)
        log_debug(f"PDF generated at {output_path}")
        return output_path

def create_pdf_builder_agent(llm):
    """Create a PDF builder agent to generate PDFs from JSON content."""
    return Agent(
        role="PDF Builder",
        goal="Transform finalized course content into professionally formatted PDF documents",
        backstory="""I am a document engineering specialist with expertise in creating 
        beautifully formatted educational materials. My background in typography, layout 
        design, and technical documentation helps me transform raw content into polished, 
        professional PDFs that enhance readability and learning retention.""",
        tools=[PDFCreatorTool()],
        verbose=True,
        memory=False,
        llm=llm,
        allow_delegation=False
    )

def generate_pdf(self, run_dir: str, use_media: bool = False, epub_kdp: bool = False):
    """Generate PDFs from JSON files in the run directory."""
    json_dir = os.path.join(run_dir, JSON_SUBDIR)
    pdf_dir = os.path.join(run_dir, PDF_SUBDIR)
    media_dir = os.path.join(run_dir, MEDIA_SUBDIR) if use_media else None
    os.makedirs(pdf_dir, exist_ok=True)
    
    journal_file = None
    lead_magnet_file = None
    edited_journal_found = False
    edited_lead_found = False
    for f in sorted(os.listdir(json_dir), reverse=True):
        if f.startswith("30day_journal_"):
            journal_file = os.path.join(json_dir, f)
            if "edited" in f:
                edited_journal_found = True
                break
    for f in sorted(os.listdir(json_dir), reverse=True):
        if f.startswith("lead_magnet_"):
            lead_magnet_file = os.path.join(json_dir, f)
            if "edited" in f:
                edited_lead_found = True
                break
    
    # Warn if no edited files, but proceed with latest
    if journal_file and not edited_journal_found:
        log_debug(f"No edited journal file found in {json_dir}, using latest: {journal_file}")
    if lead_magnet_file and not edited_lead_found:
        log_debug(f"No edited lead magnet file found in {json_dir}, using latest: {lead_magnet_file}")
    
    pdf_result = {}
    if journal_file:
        try:
            with open(journal_file, "r") as f:
                journal_data = json.load(f)
            suffix = "_epub_kdp" if epub_kdp else ""
            journal_pdf = os.path.join(pdf_dir, f"{os.path.basename(journal_file).replace('.json', '')}{suffix}.pdf")
            self.tools[0]._run(journal_data, journal_pdf, use_media, media_dir, epub_kdp)
            pdf_result["journal_pdf"] = journal_pdf
            log_debug(f"Generated journal PDF: {journal_pdf}")
        except Exception as e:
            log_debug(f"Failed to generate journal PDF: {e}")
            print(f"Error generating journal PDF: {e}")
    
    if lead_magnet_file:
        try:
            with open(lead_magnet_file, "r") as f:
                lead_magnet_data = json.load(f)
            suffix = "_epub_kdp" if epub_kdp else ""
            lead_magnet_pdf = os.path.join(pdf_dir, f"{os.path.basename(lead_magnet_file).replace('.json', '')}{suffix}.pdf")
            self.tools[0]._run(lead_magnet_data, lead_magnet_pdf, use_media, media_dir, epub_kdp)
            pdf_result["lead_magnet_pdf"] = lead_magnet_pdf
            log_debug(f"Generated lead magnet PDF: {lead_magnet_pdf}")
        except Exception as e:
            log_debug(f"Failed to generate lead magnet PDF: {e}")
            print(f"Error generating lead magnet PDF: {e}")
    
    return pdf_result
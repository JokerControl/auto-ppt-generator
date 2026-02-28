"""
MCP (Model Context Protocol) Skills for PPT Generation
This module implements various skills that can be used by the AI agent
"""
from typing import Dict, Any, List, Optional
import json
import re


class MCPSkillRegistry:
    """Registry for MCP skills"""
    
    def __init__(self):
        self.skills = {
            "ppt.structure": self.analyze_structure,
            "ppt.content": self.generate_content,
            "ppt.design": self.apply_design,
            "ppt.export": self.process_export,
            "ppt.validate": self.validate_ppt,
            "ppt.optimize": self.optimize_content,
        }
    
    async def execute(self, skill_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill by name"""
        if skill_name not in self.skills:
            return {
                "success": False,
                "error": f"Unknown skill: {skill_name}",
                "available_skills": list(self.skills.keys())
            }
        
        try:
            result = await self.skills[skill_name](parameters)
            return {
                "success": True,
                "skill_name": skill_name,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "skill_name": skill_name,
                "error": str(e)
            }
    
    # Skill implementations
    
    async def analyze_structure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill: ppt.structure
        Analyze and validate PPT structure
        """
        outline = params.get("outline", [])
        
        if not outline:
            return {
                "valid": False,
                "issues": ["Outline is empty"],
                "suggestions": ["Please provide content outline"]
            }
        
        issues = []
        suggestions = []
        
        # Check structure
        for i, page in enumerate(outline):
            if not page.get("title"):
                issues.append(f"Page {i+1} missing title")
            if not page.get("content") and not page.get("bullets"):
                issues.append(f"Page {i+1} missing content")
        
        # Analyze flow
        if len(outline) < 5:
            suggestions.append("Consider adding more content pages")
        
        # Check for introduction and conclusion
        has_intro = any(p.get("page_num") == 1 for p in outline)
        has_conclusion = len(outline) > 0
        
        if not has_intro:
            suggestions.append("Add a title/introduction page")
        
        return {
            "valid": len(issues) == 0,
            "total_pages": len(outline),
            "issues": issues,
            "suggestions": suggestions,
            "structure_score": max(0, 100 - len(issues) * 10)
        }
    
    async def generate_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill: ppt.content
        Generate detailed content for PPT pages
        """
        topic = params.get("topic", "")
        outline = params.get("outline", [])
        style = params.get("style", "professional")
        
        if not outline:
            return {
                "success": False,
                "error": "No outline provided"
            }
        
        enhanced_outline = []
        
        for page in outline:
            page_num = page.get("page_num", 1)
            title = page.get("title", "")
            bullets = page.get("bullets", [])
            
            # Enhance content based on page type
            enhanced_page = {
                "page_num": page_num,
                "title": title,
                "content": page.get("content", ""),
                "bullets": bullets,
                "notes": self._generate_speaker_notes(title, bullets, style)
            }
            
            enhanced_outline.append(enhanced_page)
        
        return {
            "success": True,
            "topic": topic,
            "enhanced_pages": enhanced_outline,
            "total_pages": len(enhanced_outline)
        }
    
    async def apply_design(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill: ppt.design
        Apply design templates and themes
        """
        theme = params.get("theme", "business")
        outline = params.get("outline", [])
        
        # Define theme configurations
        theme_configs = {
            "business": {
                "primary_color": (0, 51, 102),
                "secondary_color": (0, 102, 204),
                "font_title": "Arial",
                "font_body": "Calibri",
                "layout": "corporate",
                "logo_position": "bottom_right"
            },
            "education": {
                "primary_color": (34, 139, 34),
                "secondary_color": (85, 107, 47),
                "font_title": "Georgia",
                "font_body": "Trebuchet MS",
                "layout": "academic",
                "logo_position": "top_right"
            },
            "creative": {
                "primary_color": (128, 0, 128),
                "secondary_color": (255, 0, 128),
                "font_title": "Comic Sans MS",
                "font_body": "Verdana",
                "layout": "modern",
                "logo_position": "bottom_left"
            },
            "tech": {
                "primary_color": (0, 100, 200),
                "secondary_color": (0, 255, 150),
                "font_title": "Consolas",
                "font_body": "Segoe UI",
                "layout": "tech",
                "logo_position": "top_left"
            },
            "minimal": {
                "primary_color": (0, 0, 0),
                "secondary_color": (128, 128, 128),
                "font_title": "Helvetica",
                "font_body": "Arial",
                "layout": "minimal",
                "logo_position": "none"
            }
        }
        
        config = theme_configs.get(theme, theme_configs["business"])
        
        return {
            "success": True,
            "theme": theme,
            "config": config,
            "total_slides": len(outline)
        }
    
    async def process_export(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill: ppt.export
        Process export formats and options
        """
        format_type = params.get("format", "pptx")
        options = params.get("options", {})
        
        export_options = {
            "pptx": {
                "editable": True,
                "full_quality": True,
                "embedded_fonts": True
            },
            "pdf": {
                "editable": False,
                "full_quality": True,
                "embed_fonts": False,
                "quality": options.get("quality", "high")
            },
            "images": {
                "format": options.get("image_format", "png"),
                "resolution": options.get("resolution", "high"),
                "size": options.get("size", "original")
            }
        }
        
        config = export_options.get(format_type, export_options["pptx"])
        
        return {
            "success": True,
            "format": format_type,
            "options": config,
            "estimated_size": self._estimate_export_size(format_type, params.get("pages", 10))
        }
    
    async def validate_ppt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill: ppt.validate
        Validate PPT file and content
        """
        filepath = params.get("filepath", "")
        outline = params.get("outline", [])
        
        validation_results = {
            "file_exists": bool(filepath),
            "outline_complete": len(outline) > 0,
            "content_issues": [],
            "warnings": []
        }
        
        # Check outline completeness
        if len(outline) < 5:
            validation_results["warnings"].append("PPT has fewer than 5 slides")
        
        # Check for empty content
        for i, page in enumerate(outline):
            if not page.get("title"):
                validation_results["content_issues"].append(f"Slide {i+1}: Missing title")
            if not page.get("content") and not page.get("bullets"):
                validation_results["content_issues"].append(f"Slide {i+1}: Missing content")
        
        validation_results["valid"] = len(validation_results["content_issues"]) == 0
        
        return validation_results
    
    async def optimize_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill: ppt.optimize
        Optimize content for better presentation
        """
        outline = params.get("outline", [])
        max_bullets = params.get("max_bullets_per_slide", 6)
        target_reading_time = params.get("target_reading_time", 30)  # minutes
        
        optimized = []
        total_bullets = 0
        
        for page in outline:
            bullets = page.get("bullets", [])
            
            # Optimize bullets
            if len(bullets) > max_bullets:
                # Move excess bullets to next slide or notes
                optimized_bullets = bullets[:max_bullets]
                excess_bullets = bullets[max_bullets:]
                
                optimized_page = {
                    **page,
                    "bullets": optimized_bullets,
                    "notes": page.get("notes", "") + "\n\n" + "\n".join(excess_bullets)
                }
            else:
                optimized_page = page
            
            optimized.append(optimized_page)
            total_bullets += len(optimized_page.get("bullets", []))
        
        # Estimate reading time
        estimated_time = total_bullets * 0.5  # ~30 seconds per bullet
        
        return {
            "success": True,
            "optimized_pages": len(optimized),
            "total_bullets": total_bullets,
            "estimated_time": round(estimated_time, 1),
            "within_time_limit": estimated_time <= target_reading_time
        }
    
    # Helper methods
    
    def _generate_speaker_notes(
        self, 
        title: str, 
        bullets: List[str], 
        style: str
    ) -> str:
        """Generate speaker notes for a slide"""
        notes = f"Key points for '{title}':\n"
        
        for bullet in bullets:
            # Expand short bullets
            expanded = self._expand_bullet(bullet, style)
            notes += f"- {expanded}\n"
        
        return notes
    
    def _expand_bullet(self, bullet: str, style: str) -> str:
        """Expand a short bullet point"""
        # Add common expansions based on keywords
        if "?" in bullet:
            return bullet + " (Explain the context and significance)"
        if any(word in bullet.lower() for word in ["benefit", "advantage", "pro"]):
            return bullet + " (Provide specific examples)"
        if any(word in bullet.lower() for word in ["challenge", "problem", "issue"]):
            return bullet + " (Discuss potential solutions)"
        
        return bullet
    
    def _estimate_export_size(self, format_type: str, pages: int) -> str:
        """Estimate export file size"""
        estimates = {
            "pptx": f"{pages * 0.5:.1f} MB",
            "pdf": f"{pages * 1:.1f} MB",
            "images": f"{pages * 2:.1f} MB"
        }
        return estimates.get(format_type, "Unknown")


# Singleton instance
mcp_registry = MCPSkillRegistry()

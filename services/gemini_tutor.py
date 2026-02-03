"""
Gemini AI Tutor Service for Olympiad Math Questions in Bangla
Provides informal, friendly explanations in Bangla style
"""

import google.generativeai as genai
from config import Config
import os

class GeminiTutor:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model = None
        self.initialize()
    
    def initialize(self):
        """Initialize Gemini API"""
        if not self.api_key:
            print("⚠️  Warning: GEMINI_API_KEY not found in environment variables")
            return False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Gemini AI initialization failed: {e}")
            return False
    
    def get_system_prompt(self):
        """System prompt for Bangla informal math tutoring"""
        return """তুমি একজন বন্ধুসুলভ এবং অত্যন্ত জ্ঞানী অলিম্পিয়াড ম্যাথ টিউটর। তোমার নাম 'অলিম্পাস AI'। তোমার কাজ হল বাংলায় অনানুষ্ঠানিক (informal) ভাষায় ম্যাথ অলিম্পিয়াড প্রশ্নের গভীর ও বিস্তারিত ব্যাখ্যা দেওয়া।

ভূমিকা:
তুমি শুধু উত্তর দেবে না, বরং কেন এবং কীভাবে সমাধানটি কাজ করে তা শেখাবে। তোমার লক্ষ্য হল ছাত্রকে গণিতের সৌন্দর্য বোঝানো।

নিয়মাবলী:
1. **বিস্তারিত ব্যাখ্যা**: প্রতিটি ধাপের পেছনের যুক্তি পরিষ্কারভাবে ব্যাখ্যা কর। "কেন এই সূত্র ব্যবহার করলাম?" - এটা বুঝিয়ে বল।
2. **বাংলায় উত্তর দাও**: সম্পূর্ণ কথোপকথন বাংলায় কর। গাণিতিক টার্মগুলো ইংরেজিতে রেখে তাদের বাংলা ব্যাখ্যা দাও।
3. **বন্ধুত্বপূর্ণ ও উৎসাহী**: "তুমি" করে বল। ছাত্রের ভুল হলে উৎসাহ দাও। যেমন: "এটা খুব ভালো চেষ্টা ছিল, কিন্তু এসো দেখি অন্যভাবে ভাবা যায় কি না।"
4. **ধাপে ধাপে সমাধান**:
   - প্রথমে সমস্যাটি নিজের ভাষায় সংক্ষেপে বল।
   - এরপর সমাধানের কৌশল (Strategy) নিয়ে আলোচনা কর।
   - তারপর ধাপে ধাপে (Step-by-step) সমাধান কর।
   - শেষে উত্তরটি হাইলাইট কর।
5. **বাস্তব উদাহরণ**: বিমূর্ত বা কঠিন ধারণা বোঝাতে বাস্তব জীবনের উদাহরণ বা উপমা (Analogy) ব্যবহার কর।
6. **Socratic Method**: মাঝে মাঝে ছাত্রকে চিন্তা করতে প্রশ্ন কর। সরাসরি উত্তর না দিয়ে তাকে সঠিক পথে চালিত কর।

উত্তরের কাঠামো (Structure):
- **সূচনা**: সমস্যাটি নিয়ে একটি মজার বা উৎসাহী বাক্য।
- **বিশ্লেষণ**: সমস্যাটি আসলে কী জানতে চেয়েছে।
- **সমাধান**: পয়েন্ট করে বা প্যারাগ্রাফে বিস্তারিত সমাধান।
- **উপসংহার**: মূল বিষয়টির সারসংক্ষেপ বা একটি টিপস।

মনে রাখবে: তোমার লক্ষ্য শুধু সমস্যা সমাধান করা নয়, ছাত্রের চিন্তার দক্ষতা বৃদ্ধি করা।
"""
    
    def ask(self, question, context=None):
        """
        Ask Gemini a question about olympiad math
        Args:
            question: The math question or user query
            context: Optional previous conversation context
        Returns:
            Bangla response from Gemini
        """
        if not self.model:
            return "দুঃখিত! AI টিউটর এই মুহূর্তে উপলব্ধ নেই। অনুগ্রহ করে পরে চেষ্টা করো। (Gemini API key not configured)"
        
        try:
            # Build conversation history if context provided
            prompt = self.get_system_prompt() + "\n\n"
            
            if context:
                prompt += "আগের কথোপকথন:\n"
                for msg in context:
                    prompt += f"{msg['role']}: {msg['content']}\n"
                prompt += "\n"
            
            prompt += f"ছাত্র/ছাত্রীর প্রশ্ন: {question}\n\nউত্তর:"
            
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Error in Gemini API call: {e}")
            return f"দুঃখিত! একটা সমস্যা হয়েছে। আবার চেষ্টা করো। (Error: {str(e)})"
    
    def explain_solution(self, problem_statement, solution_english):
        """
        Translate and explain a solution in informal Bangla
        Args:
            problem_statement: The math problem
            solution_english: English solution to translate
        Returns:
            Bangla explanation
        """
        prompt = f"""{self.get_system_prompt()}
        
প্রশ্ন: {problem_statement}

ইংরেজি সমাধান: {solution_english}

এই সমাধানটি বাংলায় অনানুষ্ঠানিক (informal) ভাষায় ব্যাখ্যা কর। ধাপে ধাপে বুঝিয়ে দাও যাতে একজন অলিম্পিয়াড শিক্ষার্থী সহজে বুঝতে পারে।
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"সমাধান অনুবাদ করতে সমস্যা হয়েছে: {str(e)}"

# Global instance
gemini_tutor = GeminiTutor()

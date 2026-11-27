"""Bounded Hindi intent rules. Labels never authorize actions."""
import re
from language.hindi_normalizer import hindi_search_key
from intelligence.question_classifier import Classification


class HindiQuestionClassifier:
    RULES = (
        ('greeting', r'^(?:नमस्ते|नमस्कार|प्रणाम|आप कैसे हैं|कैसे हैं)$'),
        ('identity', r'^(?:आप कौन हैं|तुम कौन हो|आपका नाम क्या है|आपको किसने बनाया)$'),
        ('memory_retrieval', r'^(?:मेरा|मेरी|मेरे) .+(?:क्या है|क्या हैं|याद है)$'),
        ('memory_storage', r'^(?:याद रखिए|याद रखो|याद रखें)(?: |$)|^(?:मेरा|मेरी) (?:नाम|पसंदीदा रंग|कंपनी) .+ है$'),
        ('file_generation', r'(?:pdf|docx|xlsx|csv|txt|pptx|word|excel|powerpoint|पीडीएफ).*(?:बनाइए|बनाएं|बनाओ|तैयार करें|लिखिए)$'),
        ('calculation', r'\d+(?:\.\d+)?\s*(?:गुणा|भाग|जोड़|घटा|[+*/×÷-])\s*\d+|(?:गणना|हिसाब) (?:करें|कीजिए)'),
        ('document_analysis', r'\.(?:pdf|docx|xlsx|csv|txt|md|json|pptx)(?: |$).*(?:पढ़िए|पढ़ें|सारांश|विश्लेषण)'),
        ('product_knowledge', r'^(?:billnika|klubai|बिलनिका|क्लबएआई)(?: |$).*(?:क्या है|विशेषताएँ|विशेषताएं|बताइए|जानकारी)'),
        ('follow_up', r'^(?:इसके बारे में और|उसके बारे में और|और बताइए|आगे बताइए|जारी रखें)'),
        ('comparison', r'(?:में क्या अंतर है|में अंतर बताइए|की तुलना|का अंतर)'),
        ('programming', r'(?:प्रोग्राम|कोड|फंक्शन|स्क्रिप्ट|program|code|function|script).*(?:लिखिए|लिखें|बनाइए|बनाएं|सुधारें)$'),
        ('factual', r'(?:किसने|कब|कहाँ|कहां|कौन सा|कितने|कितनी)'),
        ('procedure', r'कैसे (?:सीखें|सीखना|करें|बनाएं|बनाएँ|इंस्टॉल|उपयोग|चलाएं|चलाएँ)'),
        ('explanation', r'(?:फायदे|फ़ायदे|लाभ|क्यों|समझाइए|समझाएं|कैसे काम)'),
        ('definition', r'(?:क्या है|क्या हैं|की परिभाषा)$'),
        ('writing', r'(?:लिखिए|लिखें|मसौदा बनाइए)$'),
    )

    def classify(self, text):
        q = hindi_search_key(text).rstrip(' ?!।॥.')

        if not q:
            return Classification('empty', 'No input')

        if re.match(r'^/[a-z][a-z0-9-]*(?:\s|$)', q):
            return Classification(
                'command',
                'Slash command syntax'
            )

        # Recognize numeric expressions before checking
        # for Devanagari letters.
        if re.fullmatch(
            r'\d+(?:\.\d+)?'
            r'(?:\s*[+*/×÷-]\s*\d+(?:\.\d+)?)+',
            q
        ):
            return Classification(
                'calculation',
                'Matched normalized numeric expression'
            )

        if not re.search(r'[\u0900-\u097f]', q):
            return Classification(
                'unknown',
                'No Devanagari text'
            )

        for intent, pattern in self.RULES:
            if re.search(pattern, q):
                return Classification(
                    intent,
                    'Matched Hindi intent pattern'
                )

        return Classification(
            'unknown',
            'No supported Hindi intent pattern matched'
        )
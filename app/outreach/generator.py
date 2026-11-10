from typing import Dict
from app.models import Lead

def generate_pitch(lead: Lead) -> Dict[str, str]:
    """
    Generates personalized, high-converting outreach messages
    customized specifically for the lead's type, business name, city, and industry.
    """
    contact = lead.contact_name or "Business Owner"
    biz = lead.business_name
    city = lead.city if lead.city and lead.city != "Remote / Nationwide" else "your area"
    cat = lead.category or "services"

    if lead.lead_type == "no_website":
        email_subject = f"Quick question regarding {biz}'s website in {city}"
        email_body = f"""Hi {contact},

I was looking up top-rated {cat.lower()} providers in {city} and came across {biz}. Your reputation and reviews speak for themselves!

However, I noticed you don't currently have an active, mobile-friendly website where local customers can view your services, check pricing, and book directly online.

Most local customers in {city} search on Google first, and businesses without a modern site end up losing 40-50% of high-intent calls to nearby competitors who have a simple site set up.

I build fast, professional websites specifically for local businesses like yours (takes less than 3 days, no upfront tech headache).

Would you be open to seeing a quick, 2-minute free mockup of what a clean website for {biz} could look like?

Best regards,
[Your Name]
[Your Phone Number]
[Your Portfolio Link]"""

        sms_body = f"Hi {contact}, this is [Your Name]. Saw {biz} in {city}—you do great work! Noticed you don't have a modern website yet. We build simple 1-page sites for local pros that double incoming customer calls. Would you like to see a free mockup for {biz}?"

        phone_script = f"""Caller: "Hi, is this {contact} with {biz}?"
Lead: "Yes, speaking."
Caller: "Hey {contact}! My name is [Your Name]. I came across your business while looking up {cat.lower()} in {city}. I noticed you have great local presence, but don't currently have an official website where people can book or request quotes online. I design high-converting, affordable sites for local trades here in the US. I put together a quick draft concept for {biz}—can I shoot over a quick screenshot to your email or text to see what you think?"""

    else: # seeking_website
        email_subject = f"Website Development for {biz} - Available to assist"
        email_body = f"""Hi {contact},

I saw your recent post regarding your website project for {biz}.

I specialize in building clean, fast, high-converting websites and landing pages for US businesses and entrepreneurs.

Here is what I can deliver for your project:
• Fully responsive, modern design (looks great on iPhone & desktop)
• Fast loading speed, SEO-optimized for Google search
• Contact forms, quote estimators, and online appointment booking
• Turnaround within 3-7 days with 100% satisfaction guarantee

You can check out some of my recent work here: [Your Portfolio Link]

Are you free for a quick 10-minute call or chat today to go over your vision and budget?

Best regards,
[Your Name]
[Your Phone / WhatsApp]"""

        sms_body = f"Hi {contact}! Saw your request for a website build for {biz}. I'm an independent US web designer and would love to help you bring this to life quickly and affordably. When are you free for a quick chat?"

        phone_script = f"""Caller: "Hi {contact}, my name is [Your Name]. I saw your posting regarding your website project for {biz}."
Lead: "Oh yes, what's up?"
Caller: "I specialize in building custom, responsive websites with online booking and quote forms for businesses just like yours. I reviewed your requirements and know exactly how to execute this within your timeline. Do you have 5 minutes to walk through your key goals?"""

    return {
        "email_subject": email_subject,
        "email_body": email_body,
        "sms_body": sms_body,
        "phone_script": phone_script
    }


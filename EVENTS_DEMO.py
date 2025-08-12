#!/usr/bin/env python3
"""
Events Management System Demo Script

This script demonstrates how to use the Events Management System APIs.
It shows the key workflows for creating events, managing attendees, and tracking relationships.

Run this after starting the FastAPI server to see the system in action.
"""

import requests
import json
from datetime import date, datetime
from decimal import Decimal

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
# Note: In a real scenario, you would need to authenticate and get a JWT token
# For this demo, we'll show the API structure

class EventsDemo:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            # "Authorization": "Bearer YOUR_JWT_TOKEN"  # Add when authenticated
        }
    
    def demo_event_creation(self):
        """Demonstrate creating a new event"""
        print("🎉 Creating a new event...")
        
        event_data = {
            "name": "Tech Meetup: AI in Healthcare",
            "description": "Monthly meetup discussing AI applications in healthcare",
            "event_type": "meetup",
            "event_category": "professional",
            "start_date": "2025-08-25",
            "start_time": "18:00:00",
            "end_time": "21:00:00",
            "location": "Innovation Hub",
            "venue": "Conference Room A",
            "address_city": "San Francisco",
            "address_state": "CA",
            "organizer_name": "Healthcare AI Group",
            "expected_attendees": 50,
            "cost": 25.00,
            "currency": "USD",
            "event_website": "https://healthcareai.meetup.com",
            "status": "planned"
        }
        
        print("Event Data:")
        print(json.dumps(event_data, indent=2))
        print(f"API Call: POST {self.base_url}/events")
        return event_data
    
    def demo_contact_creation(self):
        """Demonstrate creating a contact"""
        print("\n👤 Creating a contact...")
        
        contact_data = {
            "first_name": "Dr. Sarah",
            "last_name": "Johnson",
            "full_name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@healthtech.com",
            "phone": "+1-555-0123",
            "title": "Chief Medical Officer",
            "company": "HealthTech Innovations",
            "notes": "Expert in medical AI applications"
        }
        
        print("Contact Data:")
        print(json.dumps(contact_data, indent=2))
        print(f"API Call: POST {self.base_url}/contacts")
        return contact_data
    
    def demo_attendance_management(self):
        """Demonstrate adding an attendee to an event"""
        print("\n🤝 Adding attendee to event...")
        
        attendance_data = {
            "contact_id": 123,  # Would be actual contact ID
            "event_id": 456,    # Would be actual event ID
            "attendance_status": "confirmed",
            "role_at_event": "speaker",
            "invitation_method": "direct",
            "how_we_met_at_event": "Approached after their presentation on medical imaging AI",
            "conversation_highlights": "Discussed potential collaboration on medical device AI",
            "rsvp_response": "yes",
            "relationship_strength_before": 3,
            "follow_up_needed": True,
            "follow_up_notes": "Schedule follow-up meeting to discuss collaboration"
        }
        
        print("Attendance Data:")
        print(json.dumps(attendance_data, indent=2))
        print(f"API Call: POST {self.base_url}/events/456/attendees")
        return attendance_data
    
    def demo_follow_up_creation(self):
        """Demonstrate creating a follow-up action"""
        print("\n📝 Creating follow-up action...")
        
        follow_up_data = {
            "event_id": 456,
            "contact_id": 123,
            "follow_up_type": "business_discussion",
            "description": "Schedule meeting to discuss AI collaboration opportunities",
            "due_date": "2025-09-01",
            "priority": "high",
            "status": "pending"
        }
        
        print("Follow-up Data:")
        print(json.dumps(follow_up_data, indent=2))
        print(f"API Call: POST {self.base_url}/events/456/follow-ups")
        return follow_up_data
    
    def demo_event_queries(self):
        """Demonstrate various event query capabilities"""
        print("\n🔍 Event Discovery Examples:")
        
        queries = [
            "GET /events?event_type=meetup&status=planned",
            "GET /events/search?q=healthcare",
            "GET /events/upcoming?limit=10",
            "GET /events/calendar/2025/8",
            "GET /events/456?include=attendees,follow_ups",
            "GET /events/456/analytics"
        ]
        
        for query in queries:
            print(f"  📊 {query}")
    
    def demo_relationship_tracking(self):
        """Demonstrate relationship tracking features"""
        print("\n💝 Relationship Tracking Examples:")
        
        examples = [
            {
                "description": "Track new connections made at event",
                "endpoint": "GET /events/456/new-connections",
                "use_case": "Identify first-time meetings"
            },
            {
                "description": "Monitor relationship strength changes",
                "endpoint": "GET /events/456/relationship-changes",
                "use_case": "Measure networking effectiveness"
            },
            {
                "description": "Find shared events between contacts",
                "endpoint": "GET /contacts/123/shared-events/789",
                "use_case": "Discover mutual connections"
            },
            {
                "description": "Get contact's event history",
                "endpoint": "GET /contacts/123/events",
                "use_case": "View relationship timeline"
            }
        ]
        
        for example in examples:
            print(f"  🔗 {example['description']}")
            print(f"     API: {example['endpoint']}")
            print(f"     Use Case: {example['use_case']}")
            print()
    
    def demo_analytics_insights(self):
        """Demonstrate analytics capabilities"""
        print("\n📈 Analytics Example Response:")
        
        analytics_response = {
            "new_connections": 3,
            "strengthened_relationships": 5,
            "follow_ups_created": 8,
            "total_attendees": 42,
            "attendance_rate": 0.84
        }
        
        print("GET /events/456/analytics")
        print(json.dumps(analytics_response, indent=2))
        
        print("\nInsights:")
        print(f"  • Made {analytics_response['new_connections']} new connections")
        print(f"  • Strengthened {analytics_response['strengthened_relationships']} existing relationships")
        print(f"  • Created {analytics_response['follow_ups_created']} follow-up actions")
        print(f"  • {analytics_response['attendance_rate']*100:.0f}% attendance rate")
    
    def run_demo(self):
        """Run the complete demo"""
        print("=" * 60)
        print("🎉 EVENTS MANAGEMENT SYSTEM - API DEMO")
        print("=" * 60)
        
        self.demo_event_creation()
        self.demo_contact_creation()
        self.demo_attendance_management()
        self.demo_follow_up_creation()
        self.demo_event_queries()
        self.demo_relationship_tracking()
        self.demo_analytics_insights()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETE")
        print("=" * 60)
        print("\nTo use these APIs in production:")
        print("1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("2. Get authentication token via /api/v1/login")
        print("3. Include token in Authorization header")
        print("4. Use the endpoints demonstrated above")
        print("5. View full API docs at http://localhost:8000/docs")

if __name__ == "__main__":
    demo = EventsDemo()
    demo.run_demo()
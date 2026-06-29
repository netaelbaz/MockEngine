---
layout: home

hero:
  name: MockEngine SDK
  text: HTTP Mocking for Android
  tagline: Intercept, mock, and control any HTTP request from your Android app — in real time, without touching a single line of app code.
  actions:
    - theme: brand
      text: Get Started
      link: /getting-started
    - theme: alt
      text: View Examples
      link: /examples

features:
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>'
    title: Rule-Based Interception
    details: Define a URL pattern and HTTP method. Every matching request is intercepted automatically and returns your configured mock response.
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
    title: Real-Time Updates
    details: Rules sync to connected devices every 60 seconds. Enable or disable a rule from the web portal and it takes effect without a redeployment.
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/></svg>'
    title: Dual Backend Modes
    details: Full mock mode skips the real server entirely. Passthrough mode calls the real server but overrides the response — your choice, per rule.
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
    title: Analytics Dashboard
    details: Every HTTP call is logged. Track interception rates, endpoint performance, device health, and error distribution from one place.
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>'
    title: AI-Powered Mock Generation
    details: Describe the response you need in plain English. MockEngine generates realistic JSON mock data automatically — no manual JSON required.
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>'
    title: Offline-First Cache
    details: Rules are stored locally on-device using Room. Mocking works even when the device has no network connection to the MockEngine backend.
---

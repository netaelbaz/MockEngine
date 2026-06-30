# Demo

A visual walkthrough of the MockEngine portal and what you see after integrating the SDK into your Android app.

## Video Walkthrough

<video controls width="100%" style="border-radius: 8px;">
  <source src="/demo.mp4" type="video/mp4" />
</video>

---

## Dashboard

The dashboard is the main analytics hub. It has two tabs: **General** (traffic and health) and **Interception** (rule effectiveness).

### General Stats

A high-level view of total HTTP calls, device health, error distribution, request activity over time, and app version spread across connected devices.

<figure class="demo-screenshot">
  <img src="/screenshots/dashboard-general.png" alt="Dashboard — General tab showing total calls, device health, error distribution, and request activity chart" />
  <figcaption>Dashboard → General tab</figcaption>
</figure>

<figure class="demo-screenshot">
  <img src="/screenshots/dashboard-endpoint-analytics.png" alt="Dashboard — Endpoint analytics table with method, calls, avg response time, and network type breakdown" />
  <figcaption>Dashboard → Endpoint Analytics</figcaption>
</figure>

### Interception Analytics

Switch to the **Interception** tab to see how your rules are performing — which rules are getting hits, when they were last used, and which endpoints are being intercepted most.

<figure class="demo-screenshot">
  <img src="/screenshots/dashboard-interception.png" alt="Dashboard — Interception tab showing active rules count, rule effectiveness table, and endpoint interception rate" />
  <figcaption>Dashboard → Interception tab</figcaption>
</figure>

---

## Interception Rules

The **Rules** page is where you define which requests MockEngine intercepts. Each rule targets a URL pattern and HTTP method, and lets you configure the status code, response body, delay, and backend mode.

<figure class="demo-screenshot">
  <img src="/screenshots/rules.png" alt="Rules page showing a list of interception rules with method badges, endpoint pills, status codes, delays, and enable toggles" />
  <figcaption>Rules page — toggle, edit, or delete rules in real time</figcaption>
</figure>

---

## API Keys

Every app integration requires an API key. The **API Keys** page lets you generate and manage keys. Keys are shown in a truncated preview — copy the full value at generation time.

<figure class="demo-screenshot">
  <img src="/screenshots/api-keys.png" alt="API Keys page showing a table of named keys with truncated previews and copy/delete actions" />
  <figcaption>API Keys — generate and manage keys for each app integration</figcaption>
</figure>

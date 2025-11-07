# Diamond OA Journal Management System - User Guide

**Version 1.0**
**Last Updated: November 2024**

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Article Management](#article-management)
5. [A/B Testing](#ab-testing)
6. [Analytics & Insights](#analytics--insights)
7. [Personalization](#personalization)
8. [SEO Optimization](#seo-optimization)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

Welcome to the Diamond OA Journal Management System - a next-generation platform that combines the best of traditional journal management with cutting-edge AI, personalization, and analytics features.

### Key Features

✨ **10x Better Than OJS**
- Modern React 18 interface (vs OJS PHP 2005)
- Sub-second page loads (vs OJS 5-10 seconds)
- Interactive UI components
- Real-time updates via WebSocket

🎯 **Enterprise-Grade Intelligence**
- A/B testing for data-driven decisions
- AI-powered personalization
- Real-time analytics dashboard
- SEO optimization tools

🚀 **Diamond Open Access**
- 100% free to read
- 100% free to publish
- No article processing charges (APCs)
- Ethical, transparent publishing

---

## Getting Started

### Roles and Permissions

| Role | Permissions |
|------|-------------|
| **Editor-in-Chief** | Full access to all features |
| **Section Editor** | Manage manuscripts in assigned sections |
| **Reviewer** | Review assigned manuscripts |
| **Author** | Submit and track manuscripts |
| **Reader** | Browse and read articles |

### First Login

1. Navigate to your journal's URL
2. Click "Sign In" in the top navigation
3. Enter your credentials
4. You'll be redirected to your dashboard

### Dashboard Sections

After login, you'll see different dashboards based on your role:

- **Editors**: Manuscript queue, editorial tools, analytics
- **Reviewers**: Pending reviews, review history
- **Authors**: Submission status, published articles
- **Readers**: Personalized recommendations

---

## Dashboard Overview

### Editor Dashboard

**Overview Cards**
- Pending manuscripts (requires action)
- Manuscripts in review
- Accepted manuscripts
- Published articles this month

**Quick Actions**
- Create A/B test
- View analytics
- Manage themes
- Export reports

**Recent Activity**
- Latest submissions
- Recent reviews
- Editorial decisions
- System notifications

### Real-Time Metrics

At the top of your dashboard, you'll see:
- Active users (right now)
- Articles viewed (last hour)
- Downloads today
- Conversion rate

**Note**: These update every 30 seconds via WebSocket.

---

## Article Management

### Viewing Article Performance

Navigate to **Analytics > Articles** to see:

**Metrics Per Article:**
- Total views and trend (↑ or ↓)
- Downloads
- Average read time
- Completion rate (% who scrolled to end)
- Citation count
- Shares on social media

**Sorting Options:**
- Most viewed
- Highest completion rate
- Most downloaded
- Trending (biggest growth)

### Article Display Features

Our system includes NEJM/Lancet-style article formatting:

**Interactive Figures:**
- Zoom in/out (up to 5x)
- Pan by dragging
- Fullscreen lightbox mode
- Download in PNG/SVG/PDF
- Multi-panel support (A, B, C, D)
- Before/after comparison slider

**Citation Tools:**
- 7 formats: APA, MLA, Chicago, Harvard, Vancouver, BibTeX, RIS
- One-click copy
- Export to Zotero, Mendeley, EndNote
- QR code for mobile access
- Email citation

**Custom Panels:**
- Key Points summary
- Research in Context
- Clinical Implications
- Supplementary Materials

---

## A/B Testing

A/B testing lets you make data-driven decisions about your journal's design and functionality.

### Creating an A/B Test

1. Navigate to **Tools > A/B Testing**
2. Click "Create Test"
3. Fill in details:
   - **Name**: Descriptive name (e.g., "Submission Button Color")
   - **Description**: What you're testing
   - **Variants**: Create 2+ variants (one must be "Control")

**Example:**

```
Test Name: CTA Button Color Test
Description: Test which button color gets more submissions

Variants:
- Control: Blue button (current design) - 50% traffic
- Variant A: Green button - 50% traffic

Metrics:
- Submission clicks (primary)
- Page time (secondary)

Target Audience: All users
Duration: 14 days
```

4. Set traffic split (must total 100%)
5. Define success metrics
6. Click "Create and Start"

### Monitoring Tests

**Live Stats:**
- Exposures: How many users saw each variant
- Conversions: How many completed the goal
- Conversion rate: % who converted
- Statistical significance: ✓ if winner found

**Winner Detection:**

The system automatically calculates:
- P-value (< 0.05 = significant)
- Confidence interval
- Improvement over control

When a winner is detected:
1. You'll see a green "WINNER" badge
2. Recommendation: "Implement this variant"
3. Improvement: "+24.5% vs control"

### Best Practices

✅ **DO:**
- Test one change at a time
- Run for at least 7 days
- Wait for statistical significance
- Test high-traffic pages first

❌ **DON'T:**
- Stop tests early
- Make multiple changes at once
- Test on low-traffic pages
- Ignore statistical significance

### Common Tests to Run

1. **Submission Form Layout**
   - Single-page vs multi-step
   - Field order variations

2. **Call-to-Action Buttons**
   - Color variations
   - Text variations ("Submit" vs "Submit Manuscript")

3. **Article Display**
   - Single-column vs two-column
   - With/without sidebar

4. **Navigation Menu**
   - Dropdown vs mega menu
   - Position variations

---

## Analytics & Insights

### Dashboard Overview

Navigate to **Analytics > Dashboard** to see comprehensive metrics.

**Date Ranges:**
- Last 7 days
- Last 30 days (default)
- Last 90 days
- Last year

**Refresh:** Auto-refreshes every 5 minutes, or click refresh button.

### Overview Metrics

**Card 1: Total Views**
- Number of page views
- % change vs previous period
- Trend indicator (↑ or ↓)

**Card 2: Unique Visitors**
- Distinct users who visited
- % change vs previous period

**Card 3: Downloads**
- Article downloads (all formats)
- % change vs previous period

**Card 4: Avg Time on Site**
- Average session duration
- Format: MM:SS

### Trends Chart

**Visualization:**
- Line chart showing daily trends
- Toggle between: Views, Visitors, Downloads
- Hover for exact numbers
- Date labels on X-axis

**Interpretation:**
- Upward trend = growth
- Spikes = viral articles or social media
- Drops = technical issues or holidays

### Traffic Sources

**Source Breakdown:**
- Organic: Search engines (Google, PubMed)
- Direct: Typed URL or bookmarks
- Social: Twitter, Facebook, LinkedIn
- Referral: Other websites
- Email: Newsletter clicks

**Progress Bars:**
- Width = percentage
- Number = visitor count
- Color = source type

**Top Referrers:**
1. Example.com - 1,234 visits (12.3%)
2. University.edu - 890 visits (8.9%)
3. Twitter.com - 567 visits (5.7%)

### Device Breakdown

**Pie Chart:**
- Desktop: 65%
- Mobile: 28%
- Tablet: 7%

**Insights:**
- High mobile % = responsive design working
- Low mobile % = mobile experience needs improvement

### Geographic Distribution

**Top Countries:**
1. United States - 3,456 visitors (34.5%)
2. United Kingdom - 1,234 visitors (12.3%)
3. Germany - 890 visitors (8.9%)

**Top Cities:**
1. New York, USA - 456 visitors
2. London, UK - 234 visitors
3. Berlin, Germany - 189 visitors

**Use Cases:**
- Identify target regions for marketing
- Understand international reach
- Plan conference presentations

### Top Articles

**Table Columns:**
- Rank: Position by views
- Title: Article title (truncated)
- Views: Total page views
- Downloads: Download count
- Completion: % who read to end
- Trend: % change vs previous period

**Sorting:**
- Click column headers to sort
- Default: Sorted by views (descending)

**Actions:**
- Click row to view article details
- Export to CSV for reports

### Real-Time Stats

Navigate to **Analytics > Real-Time** for live data (5-minute window):

**Metrics:**
- Active users right now
- Page views per minute
- Top articles being viewed
- Active sessions by country

**Use Cases:**
- Monitor traffic spikes
- See impact of social media posts
- Track conference presentation visits
- Identify server load

---

## Personalization

### How It Works

The system learns from user behavior to provide personalized experiences:

**Data Collected:**
- Articles viewed and time spent
- Search queries
- Topics of interest
- Reading patterns
- Device preference

**Personalization Applied:**
- Homepage recommendations
- "Trending for You" section
- Email notifications (right topics, right time)
- Suggested articles sidebar
- Continue reading reminders

### User Interests

**Explicit Interests:**
- Users can manually select topics
- Weight: 0.8 (high confidence)

**Implicit Interests:**
- Inferred from behavior
- Weight: 0.3-0.7 (based on engagement)

**Interest Decay:**
- Interests gradually decrease over time
- Keeps recommendations fresh
- Formula: Exponential moving average

### Recommendation Algorithm

**Scoring Factors:**
1. **Topic Match (40%)**: Keywords in common
2. **Author Match (20%)**: Read articles by same authors
3. **Recency (20%)**: Newer articles weighted higher
4. **Popularity (10%)**: Trending articles
5. **Citation Similarity (10%)**: Cited similar papers

**Example:**

```
User interests: ["CRISPR", "gene editing", "cancer"]
Article: "CRISPR-Based Cancer Therapy"
- Topic match: 3/3 keywords = 40 points
- Recency: Published 1 week ago = 18 points
- Popularity: 500 views = 8 points
Total: 66/100 relevance score
```

### Managing Personalization

**For Editors:**
1. Navigate to **Settings > Personalization**
2. View aggregate user interests
3. Identify trending topics
4. Adjust recommendation weights

**For Users:**
1. Go to **Profile > Interests**
2. Add explicit interests
3. Remove unwanted topics
4. Adjust notification frequency

### Privacy

- Users can opt out of personalization
- Anonymous users get generic recommendations
- Data retention: 90 days
- GDPR compliant
- No data selling

---

## SEO Optimization

### SEO Score

Navigate to **Tools > SEO** to check your journal's SEO health.

**Overall Score: 0-100**
- 90-100: Excellent
- 70-89: Good
- 50-69: Needs improvement
- <50: Critical issues

**Categories:**
1. **Technical SEO (30%)**
   - HTTPS enabled
   - Canonical URLs
   - Structured data
   - Page load speed

2. **Content SEO (30%)**
   - Title length (30-60 chars)
   - Meta description (120-160 chars)
   - H1 heading (exactly one)
   - Image alt text
   - Word count (300+ words)

3. **User Experience (20%)**
   - Internal links (3+ per page)
   - Bounce rate (<70%)
   - Mobile responsive

4. **Mobile SEO (20%)**
   - Responsive design
   - Touch-friendly buttons
   - Fast mobile load time

### Issue Detection

**Critical Issues** (Red):
- Missing HTTPS
- No H1 heading
- Not mobile responsive

**Warnings** (Yellow):
- Title too long/short
- Missing alt text
- Slow page load

**Info** (Blue):
- Best practice recommendations
- Optimization opportunities

### Auto-Optimization

The system automatically:

**✅ Meta Tags:**
- Title: Auto-truncated to 60 chars at word boundary
- Description: Extracted from abstract (160 chars)
- Keywords: Top 10 from title + abstract

**✅ Structured Data:**
- ScholarlyArticle schema
- Author entities with ORCID
- Publisher information
- DOI as identifier

**✅ Open Graph:**
- og:title, og:description
- og:image (cover or default)
- og:type = "article"

**✅ Twitter Cards:**
- twitter:card = "summary_large_image"
- twitter:title, twitter:description
- twitter:image

### XML Sitemap

**Auto-Generated:**
- Updated daily at 2 AM
- Includes all published articles
- Priority: 1.0 (articles), 0.8 (issues), 0.5 (pages)
- Change frequency: weekly

**Access:**
- URL: `/sitemap.xml`
- Submit to Google Search Console
- Submit to Bing Webmaster Tools

### Robots.txt

**Default Configuration:**
```
User-agent: *
Allow: /articles/
Allow: /issues/
Disallow: /api/
Disallow: /dashboard/
Sitemap: https://yourjournal.com/sitemap.xml
```

**Customization:**
1. Navigate to **Settings > SEO > Robots.txt**
2. Edit rules
3. Save and deploy

---

## Advanced Features

### 3D Cover Flip

**Usage:**
- Hover over issue covers to flip
- Front: Cover image + issue info
- Back: Table of contents
- Click to view full issue

**Customization:**
1. Navigate to **Issues > Settings**
2. Upload cover image (recommended: 800x1200px)
3. Set flip animation speed
4. Choose auto-flip (hover) or click-to-flip

### Mega Navigation Menu

**Features:**
- Dropdown categories
- Instant search with live results
- User menu with dashboard access
- Sticky header (hides on scroll down, shows on scroll up)
- Mobile hamburger menu

**Customization:**
1. Navigate to **Settings > Navigation**
2. Add/remove menu items
3. Reorder categories
4. Set icons
5. Configure mega menu panels

### Homepage Widgets

**Available Widgets:**
1. Journal Stats (views, downloads, impact)
2. Announcements (important news)
3. Trending Articles (hot, rising, steady)
4. Popular Topics (tag cloud)
5. Quick Actions (submit, review, browse)
6. Recent Articles (latest publications)
7. Upcoming Events (conferences, webinars)
8. Featured Issue (current issue spotlight)

**Customization:**
1. Navigate to **Settings > Homepage**
2. Drag & drop widgets to reorder
3. Enable/disable widgets
4. Configure widget settings
5. Preview changes

### Interactive Figures

**Features:**
- Zoom: 0.5x to 5x
- Pan: Drag to move
- Lightbox: Fullscreen mode
- Download: PNG, SVG, PDF
- Multi-panel: Switch between A, B, C, D
- Compare: Before/after slider

**Author Guidelines:**
- Upload high-resolution images (min 1200px width)
- Provide descriptive captions
- Label panels clearly (A, B, C, D)
- Include scale bars where relevant

### Citation Tools

**Formats Supported:**
- APA 7th Edition
- MLA 9th Edition
- Chicago Manual of Style
- Harvard Referencing
- Vancouver System
- BibTeX (for LaTeX)
- RIS (for reference managers)

**Export Options:**
- One-click copy to clipboard
- Download .bib file
- Download .ris file
- Email citation
- Print citation
- QR code for mobile

**Reference Manager Integration:**
- Zotero: One-click add
- Mendeley: Direct import
- EndNote: RIS file download

---

## Troubleshooting

### Common Issues

#### Dashboard Not Loading

**Symptoms:**
- Blank screen
- Loading spinner forever
- Error message

**Solutions:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Try incognito/private mode
3. Check internet connection
4. Try different browser
5. Contact support if persists

#### Analytics Not Updating

**Symptoms:**
- Stale data (old dates)
- Missing metrics
- "No data" message

**Solutions:**
1. Click refresh button
2. Check date range filter
3. Verify Redis is running (`docker-compose ps`)
4. Check backend logs (`docker-compose logs backend`)

#### A/B Test Not Tracking

**Symptoms:**
- Zero exposures
- No conversions
- Status stuck on "draft"

**Solutions:**
1. Verify test is "active" (not draft)
2. Check traffic split sums to 100%
3. Clear Redis cache
4. Check browser console for errors
5. Verify WebSocket connection

#### Personalization Not Working

**Symptoms:**
- Generic recommendations
- No "For You" section
- Same content for all users

**Solutions:**
1. Verify user is logged in
2. Check if personalization is enabled
3. User needs 3+ article views to get recommendations
4. Allow 24 hours for initial profile building

#### Slow Page Loads

**Symptoms:**
- Pages take 3+ seconds to load
- Images loading slowly
- Dashboard lagging

**Solutions:**
1. Check network tab in browser DevTools
2. Verify Redis is running (caching disabled?)
3. Check server resources (CPU, RAM)
4. Enable CDN for static assets
5. Compress images before upload

###Browser Compatibility

**Supported Browsers:**
- ✅ Chrome 90+ (recommended)
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ❌ Internet Explorer (not supported)

**Mobile Browsers:**
- ✅ Safari iOS 14+
- ✅ Chrome Android 90+
- ✅ Samsung Internet 14+

### Performance Tips

**For Best Performance:**
1. Use Chrome or Firefox latest version
2. Enable hardware acceleration
3. Close unused tabs
4. Clear cache monthly
5. Use high-speed internet

**Server Performance:**
1. Monitor Redis memory usage
2. Scale horizontally if needed
3. Use CDN for static assets
4. Enable gzip compression
5. Optimize database queries

---

## Getting Help

### Resources

📚 **Documentation:**
- User Guide (this document)
- API Documentation: `/docs`
- Developer Guide: `/docs/developer-guide.md`
- OJS Migration Guide: `/docs/ojs-migration.md`

💬 **Support Channels:**
- Email: support@yourjournal.com
- Live Chat: Click button in bottom-right
- Community Forum: forum.yourjournal.com
- GitHub Issues: github.com/yourjournal/issues

🎓 **Training:**
- Video Tutorials: yourjournal.com/training
- Webinars: Monthly (first Tuesday)
- One-on-one Training: Contact support

### Contact Information

**Technical Support:**
- Email: tech@yourjournal.com
- Response Time: 24 hours
- Priority Support: Available for editors

**Editorial Support:**
- Email: editorial@yourjournal.com
- Response Time: 48 hours
- Office Hours: Mon-Fri 9am-5pm EST

---

## Glossary

**A/B Testing**: Method of comparing two versions to see which performs better

**Bounce Rate**: Percentage of visitors who leave after viewing only one page

**Conversion**: Desired action completed (e.g., form submission, download)

**Engagement**: How users interact with content (time, scroll, clicks)

**Exposure**: When a user sees a particular variant in an A/B test

**Interest Weight**: 0-1 score indicating strength of user interest in a topic

**P-value**: Statistical measure; <0.05 means result is significant

**Redis**: In-memory database used for caching and real-time features

**Statistical Significance**: Result unlikely due to chance (95% confidence)

**WebSocket**: Technology for real-time two-way communication

---

## Appendix

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + K | Open search |
| Ctrl + / | Toggle sidebar |
| Ctrl + D | Go to dashboard |
| Ctrl + S | Save changes |
| Esc | Close modal |
| ? | Show shortcuts |

### API Endpoints

For developers integrating with the system:

**Base URL:** `https://yourjournal.com/api/v1`

**Authentication:** Bearer token in Authorization header

**Key Endpoints:**
- `GET /articles`: List articles
- `POST /ab-testing/exposure`: Track A/B test
- `GET /personalization/recommendations`: Get recommendations
- `GET /analytics/dashboard`: Get analytics data

Full API docs: `/api/v1/docs`

---

**Document Version:** 1.0
**Last Updated:** November 2024
**For Support:** support@yourjournal.com

# Sentinel Frontend

> Autonomous AI Risk Engine for Stellar - Dashboard & Command Center

## 🎨 Design Philosophy

- **Strict Black & White Theme**: Monochrome aesthetic with no colors
- **Modern & Professional**: Clean, premium design that feels state-of-the-art
- **Smooth Animations**: Parallax scrolling, hover effects, and micro-interactions
- **Deployment-Ready**: Optimized for production from the start

## 🛠️ Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Fonts**: Geist Sans & Geist Mono

## 🚀 Getting Started

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the homepage.

### Build for Production

```bash
npm run build
npm start
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with fonts & metadata
│   ├── page.tsx            # Homepage (landing page)
│   └── globals.css         # Black & white theme + Tailwind config
├── components/
│   └── ui/                 # shadcn/ui components
│       ├── button.tsx
│       └── card.tsx
├── lib/
│   └── utils.ts            # Utility functions
└── public/                 # Static assets
```

## 🎯 Current Features

### Homepage Sections

1. **Hero Section**
   - Animated gradient text
   - Parallax scrolling effect
   - Key stats (99.8% detection, <3s response, 24/7 autonomous)
   - CTA buttons

2. **Features Grid**
   - AI Detection
   - Cryptographic Oracle
   - Smart Contracts
   - Live Dashboard

3. **How It Works**
   - 5-step flow visualization
   - Transaction → Analysis → Oracle → On-Chain → Enforce

4. **CTA Section**
   - High-contrast black/white inverted design
   - Trial & sales CTAs

5. **Footer**
   - Product, Developer, Company links
   - Branding consistency

## 🎨 Color Palette

### Light Mode
- Background: `#FFFFFF`
- Foreground: `#000000`
- Muted: `#F5F5F5`
- Border: `#E5E5E5`

### Dark Mode
- Background: `#000000`
- Foreground: `#FFFFFF`
- Card: `#0A0A0A`
- Border: `#333333`

## 🔜 Next Steps

- [ ] Build Dashboard page with real-time data
- [ ] Add wallet risk visualization
- [ ] Create network graph component (D3.js)
- [ ] Add alert/enforcement event feed
- [ ] Connect to backend API
- [ ] Implement WebSocket for live updates

## 📝 Development Notes

- All components use strict black/white theme
- Hover states use opacity transitions
- Responsive design (mobile-first)
- SEO optimized with proper metadata
- Production-ready build configuration

## 🌐 Deployment

This frontend is ready to deploy on:
- Vercel (recommended)
- Netlify
- AWS Amplify
- Any static hosting platform

### Environment Variables

Create `.env.local` for API endpoints:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📄 License

Built for Stellar Hackathon 2026

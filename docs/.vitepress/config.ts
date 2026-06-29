import { defineConfig } from 'vitepress';

export default defineConfig({
  lang: 'en-US',
  title: 'MockEngine SDK',
  description: 'HTTP Mocking for Android — intercept, mock, and control any HTTP request in real time.',
  base: '/MockEngine/',

  themeConfig: {
    nav: [
      { text: 'Guide', link: '/introduction' },
      { text: 'Examples', link: '/examples' },
      { text: 'FAQ', link: '/faq' },
    ],

    sidebar: [
      {
        text: 'Overview',
        items: [
          { text: 'Introduction', link: '/introduction' },
          { text: 'Who Is It For?', link: '/who-is-it-for' },
        ],
      },
      {
        text: 'Setup',
        items: [
          { text: 'Getting Started', link: '/getting-started' },
          { text: 'How to Use', link: '/how-to-use' },
        ],
      },
      {
        text: 'Deep Dive',
        items: [
          { text: 'Implementation', link: '/implementation' },
          { text: 'Examples', link: '/examples' },
        ],
      },
      {
        text: 'Help',
        items: [
          { text: 'Troubleshooting', link: '/troubleshooting' },
          { text: 'FAQ', link: '/faq' },
        ],
      },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/netaelbaz/MockEngine' },
    ],

    footer: {
      message: 'MockEngine SDK',
      copyright: 'Copyright © 2026',
    },
  },
});

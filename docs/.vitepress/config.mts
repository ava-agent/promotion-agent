import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Promotion Agent',
  description: 'Cross-platform social media publishing guide — curated tools & workflows for 11+ platforms',
  base: '/promotion-agent/',
  head: [
    ['meta', { property: 'og:title', content: 'Promotion Agent — Cross-Platform Publishing Guide' }],
    ['meta', { property: 'og:description', content: 'Curated tools & workflows for cross-posting to 11+ social media platforms' }],
    ['meta', { property: 'og:image', content: '/promotion-agent/images/hero-banner.png' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
  ],
  themeConfig: {
    logo: '/images/hero-banner.png',
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Platforms', link: '/platforms/overview' },
      { text: 'Reference', link: '/reference/cli' },
      {
        text: 'Links',
        items: [
          { text: 'GitHub', link: 'https://github.com/kevinten10/promotion-agent' },
          { text: 'Postiz', link: 'https://github.com/gitroomhq/postiz-app' },
          { text: 'blog-auto-publishing-tools', link: 'https://github.com/ddean2009/blog-auto-publishing-tools' },
        ]
      }
    ],
    sidebar: {
      '/guide/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/guide/getting-started' },
            { text: 'Tool Selection', link: '/guide/tool-selection' },
            { text: 'Architecture', link: '/guide/architecture' },
          ]
        },
        {
          text: 'Workflows',
          items: [
            { text: 'Chinese Platforms', link: '/guide/chinese-platforms' },
            { text: 'International Platforms', link: '/guide/international-platforms' },
            { text: 'GitHub Automation', link: '/guide/github-automation' },
          ]
        }
      ],
      '/platforms/': [
        {
          text: 'Platforms',
          items: [
            { text: 'Overview', link: '/platforms/overview' },
            { text: 'Chinese Platforms', link: '/platforms/chinese' },
            { text: 'International Platforms', link: '/platforms/international' },
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'CLI Commands', link: '/reference/cli' },
            { text: 'Platform Rules', link: '/reference/platform-rules' },
            { text: 'Resources', link: '/reference/resources' },
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/kevinten10/promotion-agent' }
    ],
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present kevinten10'
    },
    search: {
      provider: 'local'
    },
    editLink: {
      pattern: 'https://github.com/kevinten10/promotion-agent/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    }
  }
})

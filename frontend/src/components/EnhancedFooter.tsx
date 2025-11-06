import React from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import {
  EnvelopeIcon,
  MapPinIcon,
  PhoneIcon,
} from '@heroicons/react/24/outline';

const EnhancedFooter: React.FC = () => {
  const { currentTheme } = useTheme();

  const footerLinks = {
    about: [
      { name: 'About Us', href: '/about' },
      { name: 'Editorial Board', href: '/editorial-board' },
      { name: 'Policies', href: '/policies' },
      { name: 'Open Access', href: '/open-access' },
    ],
    authors: [
      { name: 'Author Guidelines', href: '/author-guidelines' },
      { name: 'Submission Process', href: '/submission-process' },
      { name: 'Publication Ethics', href: '/ethics' },
      { name: 'FAQ', href: '/faq' },
    ],
    resources: [
      { name: 'Browse Articles', href: '/articles' },
      { name: 'Search', href: '/search' },
      { name: 'Indexing', href: '/indexing' },
      { name: 'Archive', href: '/archive' },
    ],
    legal: [
      { name: 'Privacy Policy', href: '/privacy' },
      { name: 'Terms of Service', href: '/terms' },
      { name: 'Cookie Policy', href: '/cookies' },
      { name: 'Accessibility', href: '/accessibility' },
    ],
  };

  const socialLinks = [
    { name: 'Twitter', href: '#', icon: '𝕏' },
    { name: 'LinkedIn', href: '#', icon: 'in' },
    { name: 'GitHub', href: '#', icon: '' },
  ];

  return (
    <footer
      className="border-t"
      style={{
        backgroundColor: currentTheme.colors.gray[900],
        borderColor: currentTheme.colors.gray[800],
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main footer content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand section */}
          <div className="lg:col-span-2">
            <div className="flex items-center mb-4">
              <div
                className="h-10 w-10 rounded-lg flex items-center justify-center"
                style={{
                  background: `linear-gradient(135deg, ${currentTheme.colors.primary[500]}, ${currentTheme.colors.primary[700]})`,
                }}
              >
                <span className="text-xl font-bold text-white">J</span>
              </div>
              <span
                className="ml-3 text-xl font-bold"
                style={{ color: currentTheme.colors.gray[100] }}
              >
                Diamond OA Journal
              </span>
            </div>
            <p
              className="text-sm mb-4 max-w-md"
              style={{ color: currentTheme.colors.gray[400] }}
            >
              A diamond open access journal committed to making research freely available to all.
              No author fees, no reader fees, just quality peer-reviewed research.
            </p>

            {/* Contact info */}
            <div className="space-y-2 text-sm">
              <div className="flex items-center" style={{ color: currentTheme.colors.gray[400] }}>
                <EnvelopeIcon className="h-4 w-4 mr-2" />
                <a href="mailto:info@journal.org" className="hover:text-white transition-colors duration-200">
                  info@journal.org
                </a>
              </div>
              <div className="flex items-center" style={{ color: currentTheme.colors.gray[400] }}>
                <PhoneIcon className="h-4 w-4 mr-2" />
                <span>+1 (555) 123-4567</span>
              </div>
              <div className="flex items-start" style={{ color: currentTheme.colors.gray[400] }}>
                <MapPinIcon className="h-4 w-4 mr-2 mt-0.5" />
                <span>123 Academic Way<br />Research City, RC 12345</span>
              </div>
            </div>

            {/* Social links */}
            <div className="flex items-center space-x-4 mt-4">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  className="h-8 w-8 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
                  style={{
                    backgroundColor: currentTheme.colors.gray[800],
                    color: currentTheme.colors.gray[400],
                  }}
                  aria-label={social.name}
                >
                  <span className="text-sm font-bold">{social.icon}</span>
                </a>
              ))}
            </div>
          </div>

          {/* About */}
          <div>
            <h3
              className="text-sm font-semibold uppercase tracking-wider mb-4"
              style={{ color: currentTheme.colors.gray[200] }}
            >
              About
            </h3>
            <ul className="space-y-2">
              {footerLinks.about.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm transition-colors duration-200 hover:text-white"
                    style={{ color: currentTheme.colors.gray[400] }}
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* For Authors */}
          <div>
            <h3
              className="text-sm font-semibold uppercase tracking-wider mb-4"
              style={{ color: currentTheme.colors.gray[200] }}
            >
              For Authors
            </h3>
            <ul className="space-y-2">
              {footerLinks.authors.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm transition-colors duration-200 hover:text-white"
                    style={{ color: currentTheme.colors.gray[400] }}
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3
              className="text-sm font-semibold uppercase tracking-wider mb-4"
              style={{ color: currentTheme.colors.gray[200] }}
            >
              Resources
            </h3>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm transition-colors duration-200 hover:text-white"
                    style={{ color: currentTheme.colors.gray[400] }}
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div
          className="pt-8 border-t flex flex-col md:flex-row justify-between items-center"
          style={{ borderColor: currentTheme.colors.gray[800] }}
        >
          <div className="text-sm mb-4 md:mb-0" style={{ color: currentTheme.colors.gray[500] }}>
            <p>
              &copy; {new Date().getFullYear()} Diamond Open Access Journal. All content is{' '}
              <a
                href="https://creativecommons.org/licenses/by/4.0/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-white transition-colors duration-200"
                style={{ color: currentTheme.colors.primary[400] }}
              >
                CC BY 4.0
              </a>{' '}
              licensed.
            </p>
          </div>

          <div className="flex items-center space-x-6 text-sm">
            {footerLinks.legal.map((link) => (
              <Link
                key={link.name}
                to={link.href}
                className="transition-colors duration-200 hover:text-white"
                style={{ color: currentTheme.colors.gray[500] }}
              >
                {link.name}
              </Link>
            ))}
          </div>
        </div>

        {/* Indexing badges */}
        <div className="mt-8 pt-8 border-t" style={{ borderColor: currentTheme.colors.gray[800] }}>
          <div className="flex flex-wrap items-center justify-center gap-6">
            <div
              className="text-xs text-center px-4 py-2 rounded-md"
              style={{ backgroundColor: currentTheme.colors.gray[800], color: currentTheme.colors.gray[400] }}
            >
              Indexed in <strong>PubMed</strong>
            </div>
            <div
              className="text-xs text-center px-4 py-2 rounded-md"
              style={{ backgroundColor: currentTheme.colors.gray[800], color: currentTheme.colors.gray[400] }}
            >
              Indexed in <strong>Scopus</strong>
            </div>
            <div
              className="text-xs text-center px-4 py-2 rounded-md"
              style={{ backgroundColor: currentTheme.colors.gray[800], color: currentTheme.colors.gray[400] }}
            >
              Indexed in <strong>Web of Science</strong>
            </div>
            <div
              className="text-xs text-center px-4 py-2 rounded-md"
              style={{ backgroundColor: currentTheme.colors.gray[800], color: currentTheme.colors.gray[400] }}
            >
              <strong>DOAJ</strong> Certified
            </div>
            <div
              className="text-xs text-center px-4 py-2 rounded-md"
              style={{ backgroundColor: currentTheme.colors.gray[800], color: currentTheme.colors.gray[400] }}
            >
              DOI registered via <strong>Crossref</strong>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default EnhancedFooter;

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { logout } from '../../store/slices/authSlice';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  React.useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-maroon border-b border-maroon-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-3">
                <span className="text-2xl font-bold text-white">
                  A11yomatic
                </span>
                <span className="text-sm text-gray-200 border-l border-gray-300 pl-3">
                  Texas A&M University
                </span>
              </Link>
              <nav className="flex space-x-4">
                <Link
                  to="/"
                  className="px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-maroon-light"
                >
                  Dashboard
                </Link>
                <Link
                  to="/upload"
                  className="px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-maroon-light"
                >
                  Upload PDF
                </Link>
              </nav>
            </div>
            <div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-maroon-light hover:bg-maroon-dark rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-dark-800 border-t border-dark-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-400">
            <div>
              <h3 className="text-white font-semibold mb-2">A11yomatic</h3>
              <p>PDF Accessibility Remediation Tool</p>
              <p className="mt-1">Texas A&M University</p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">Resources</h3>
              <ul className="space-y-1">
                <li>
                  <a href="https://www.tamu.edu" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500">
                    Texas A&M Home
                  </a>
                </li>
                <li>
                  <a href="https://www.tamu.edu/statements/index.html" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500">
                    Site Policies
                  </a>
                </li>
                <li>
                  <a href="https://www.tamu.edu/contact.html" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">Accessibility</h3>
              <ul className="space-y-1">
                <li>
                  <a href="https://www.tamu.edu/accessibility/" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500">
                    Accessibility Policy
                  </a>
                </li>
                <li>
                  <a href="https://www.tamus.edu/legal/state-link-policy/" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500">
                    State Link Policy
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-dark-700 text-center text-xs text-gray-500">
            <p>© {new Date().getFullYear()} Texas A&M University. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;



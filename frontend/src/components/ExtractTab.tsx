import { useState } from 'react';
import { extractRecipe } from '../api/client';
import type { RecipeDetail } from '../types';
import RecipeDisplay from './RecipeDisplay';

export default function ExtractTab() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [cached, setCached] = useState(false);

  const handleExtract = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    setRecipe(null);
    setCached(false);

    try {
      const res = await extractRecipe(url.trim());
      if (res.success && res.recipe) {
        setRecipe(res.recipe);
        setCached(res.cached);
      } else {
        setError('Extraction failed. Please try again.');
      }
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Failed to extract recipe. Check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="extract-hero">
        <h1>Extract Any <span>Recipe</span> Instantly</h1>
        <p>Paste a recipe blog URL and let AI extract structured data, nutrition info, substitutions, and more.</p>

        <form className="url-form" onSubmit={handleExtract}>
          <input
            id="recipe-url-input"
            className="url-input"
            type="url"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://www.allrecipes.com/recipe/..."
            disabled={loading}
          />
          <button
            id="extract-btn"
            className="extract-btn"
            type="submit"
            disabled={loading || !url.trim()}
          >
            {loading ? 'Extracting...' : 'Extract Recipe'}
          </button>
        </form>
      </div>

      {error && (
        <div className="status-message error" style={{ maxWidth: '780px', margin: '0 auto 1.5rem' }}>
          <span className="icon-warning">!</span> {error}
        </div>
      )}

      {cached && recipe && (
        <div className="status-message cached" style={{ maxWidth: '780px', margin: '0 auto 1.5rem' }}>
          <span className="icon-info">i</span> Loaded from cache — this URL was previously extracted.
        </div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="spinner" />
          <p style={{ color: 'var(--accent-green)', fontWeight: 600 }}>Processing your recipe…</p>
          <div className="loading-steps">
            <div className="loading-step">Fetching page content...</div>
            <div className="loading-step">Parsing HTML structure...</div>
            <div className="loading-step">Analyzing with Gemini AI...</div>
            <div className="loading-step">Saving to database...</div>
          </div>
        </div>
      )}

      {recipe && !loading && <RecipeDisplay recipe={recipe} />}
    </div>
  );
}

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Navbar } from '@/components/Navbar'
import { Home } from '@/pages/Home'
import { Personas } from '@/pages/Personas'
import { Assistant } from '@/pages/Assistant'
import { Analytics } from '@/pages/Analytics'
import { Admin } from '@/pages/Admin'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/personas" element={<Personas />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            className: 'bg-white shadow-lg border border-green-200',
          }}
        />
      </div>
    </Router>
  )
}

export default App
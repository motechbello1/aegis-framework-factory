import React from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Ingest from './pages/Ingest'
import ReviewQueue from './pages/ReviewQueue'
import RunDetail from './pages/RunDetail'
import Catalogue from './pages/Catalogue'
import Published from './pages/Published'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="ingest" element={<Ingest />} />
        <Route path="review" element={<ReviewQueue />} />
        <Route path="controls" element={<Catalogue />} />
        <Route path="published" element={<Published />} />
        <Route path="runs/:runId" element={<RunDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

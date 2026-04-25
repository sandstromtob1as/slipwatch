'use client';

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardHeader,
  CardMedia,
  Button,
  Chip,
  Box,
  Typography,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

interface ShapResult {
  incident_id: number;
  verdict: string;
  attribution: Record<string, number>;
  features: Record<string, string>;
}

interface Incident {
  id: number;
  timestamp: string;
  location: string;
  triggered_by: string[];
  last_upright_position: string;
  image_url: string | null;
  sms_message: string | null;
  shap_ready: boolean;
  shap?: ShapResult;
}

const API_URL = 'http://localhost:8000';

export default function Home() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selected, setSelected] = useState<Incident | null>(null);
  const [apiOnline, setApiOnline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [handledIds, setHandledIds] = useState<number[]>([]);

  const handleMarkAsHandled = (incident: Incident) => {
  // add to handled IDs
  setHandledIds((prev) => [...prev, incident.id]);

  // remove immediately from UI
  setIncidents((prev) => prev.filter((i) => i.id !== incident.id));

  // close dialog if open
  if (selected?.id === incident.id) {
    setSelected(null);
  }

  // save to localStorage (your existing logic)
  const existing = JSON.parse(localStorage.getItem('alert-history') || '[]');

  const newEntry = {
    id: incident.id,
    personName: incident.triggered_by?.[0] || 'Unknown',
    timestamp: incident.timestamp,
    location: incident.location,
    status: 'Resolved',
    notes: incident.sms_message || 'Handled from overview page',
  };

  const updated = [newEntry, ...existing];
  localStorage.setItem('alert-history', JSON.stringify(updated));
};

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const res = await fetch(`${API_URL}/incidents`);
        const data = await res.json();

        // 🚀 FILTER OUT HANDLED ONES
        const filtered = data.filter(
          (incident: Incident) => !handledIds.includes(incident.id)
        );

        setIncidents(filtered);
        setApiOnline(true);
        setLastUpdated(new Date());

        if (selected) {
          const updated = filtered.find((i: Incident) => i.id === selected.id);
          if (updated) setSelected(updated);
        }
      } catch {
        setApiOnline(false);
      }
    };

    fetchIncidents();
      const interval = setInterval(fetchIncidents, 5000);
      return () => clearInterval(interval);
    }, [selected?.id, handledIds]);

  return (
    <div className="min-h-screen py-8">
      <Container maxWidth="lg">
        <Box className="mb-8 flex items-start justify-between">
          <Box>
            <Typography variant="h2" className="font-bold text-white mb-2">
              Overview
            </Typography>
            <Typography variant="body1" className="text-gray-300">
              Real-time fall alerts with AI analysis.
            </Typography>
          </Box>
          <Box className="text-right flex flex-col items-end gap-1">
            <Chip
              icon={apiOnline ? <CheckCircleIcon /> : <WarningIcon />}
              label={apiOnline ? 'System Online' : 'System Offline'}
              color={apiOnline ? 'success' : 'error'}
              size="small"
            />
            <Typography variant="caption" className="text-gray-500">
              Updated {lastUpdated.toLocaleTimeString()}
            </Typography>
          </Box>
        </Box>

        {incidents.length > 0 ? (
          <Box className="flex flex-col gap-6">
            {incidents.map((incident) => (
              <Card
                key={incident.id}
                sx={{ backgroundColor: '#1f2937', borderColor: '#374151' }}
                className="border border-gray-700 shadow-lg"
              >
                <Box className="lg:flex">
                  <Box className="lg:w-2/3 h-64 lg:h-auto bg-gray-800 flex items-center justify-center overflow-hidden relative">
                    {incident.image_url ? (
                      <img
                        src={incident.image_url}
                        alt="Fall detected"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Typography className="text-gray-500">No image</Typography>
                    )}
                    <Box className="absolute top-3 left-3">
                      <Chip
                        icon={<WarningIcon />}
                        label="FALL DETECTED"
                        color="error"
                        size="small"
                      />
                    </Box>
                  </Box>

                  <Box className="p-6 lg:w-1/3 flex flex-col gap-4">
                    <Box>
                      <Typography variant="caption" className="text-gray-400 flex items-center gap-1">
                        <AccessTimeIcon fontSize="small" /> {incident.timestamp}
                      </Typography>
                      <Typography variant="caption" className="text-gray-400 flex items-center gap-1 mt-1">
                        <LocationOnIcon fontSize="small" /> {incident.location}
                      </Typography>
                    </Box>

                    {incident.sms_message && (
                      <Box>
                        <Typography variant="subtitle2" className="font-semibold text-gray-100 mb-1">
                          AI Analysis
                        </Typography>
                        <Typography
                          variant="body2"
                          className="text-gray-300 p-3 rounded-md bg-blue-900 border-l-4 border-blue-500"
                        >
                          {incident.sms_message}
                        </Typography>
                      </Box>
                    )}

                    <Box>
                      <Typography variant="subtitle2" className="font-semibold text-gray-100 mb-1">
                        Triggered by
                      </Typography>
                      <Box className="flex flex-wrap gap-1">
                        {incident.triggered_by.map((t, i) => (
                          <Chip
                            key={i}
                            label={t}
                            size="small"
                            sx={{ backgroundColor: '#374151', color: '#d1d5db', fontSize: '0.7rem' }}
                          />
                        ))}
                      </Box>
                    </Box>

                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => setSelected(incident)}
                      className="mt-auto"
                    >
                      View Details
                    </Button>
                    <Button
                      variant="contained"
                      color="success"
                      fullWidth
                      onClick={() => handleMarkAsHandled(incident)}
                    >
                      Mark as Handled
                    </Button>
                  </Box>
                </Box>
              </Card>
            ))}
          </Box>
        ) : (
          <Card sx={{ backgroundColor: '#1f2937' }} className="p-12 text-center border border-gray-700">
            <CheckCircleIcon sx={{ fontSize: 48, color: '#4ade80', marginBottom: 2 }} />
            <Typography variant="h6" className="text-gray-300">
              No falls detected — system is monitoring
            </Typography>
          </Card>
        )}
      </Container>

      {/* Details Dialog */}
      <Dialog
        open={!!selected}
        onClose={() => setSelected(null)}
        maxWidth="sm"
        fullWidth
        sx={{ '& .MuiDialog-paper': { backgroundColor: '#1f2937', color: '#fff' } }}
      >
        {selected && (
          <>
            <DialogTitle className="bg-red-900 border-b-2 border-red-500">
              <Box className="flex items-center gap-2">
                <WarningIcon className="text-red-400" />
                <Typography variant="h6" className="font-bold text-white">
                  Incident Details
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent className="pt-4">
              <Box className="flex flex-col gap-4 mt-2">

                {/* Image */}
                {selected.image_url && (
                  <img src={selected.image_url} alt="Fall" className="w-full rounded-lg" />
                )}

                {/* Basic info */}
                <Box>
                  <Typography variant="subtitle2" className="text-gray-400">Time</Typography>
                  <Typography variant="body2" className="text-white">{selected.timestamp}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" className="text-gray-400">Location</Typography>
                  <Typography variant="body2" className="text-white">{selected.location}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" className="text-gray-400">Last upright</Typography>
                  <Typography variant="body2" className="text-white">{selected.last_upright_position}</Typography>
                </Box>

                {/* Triggered by */}
                <Box>
                  <Typography variant="subtitle2" className="text-gray-400 mb-1">Triggered by</Typography>
                  <Box className="flex flex-wrap gap-1">
                    {selected.triggered_by.map((t, i) => (
                      <Chip key={i} label={t} size="small" sx={{ backgroundColor: '#374151', color: '#d1d5db' }} />
                    ))}
                  </Box>
                </Box>

                {/* SMS */}
                {selected.sms_message && (
                  <Box>
                    <Typography variant="subtitle2" className="text-gray-400 mb-1">SMS sent to relative</Typography>
                    <Typography variant="body2" className="text-gray-300 p-3 rounded bg-blue-900">
                      {selected.sms_message}
                    </Typography>
                  </Box>
                )}

                {/* ── llmSHAP XAI Block ── */}
                <Box>
                  <Typography variant="subtitle2" className="text-gray-400 mb-2">
                    Why AI flagged this as a fall
                  </Typography>

                  {selected.shap_ready && selected.shap ? (
                    <Box className="p-3 rounded bg-gray-900">
                      {/* Verdict */}
                      <Typography variant="caption" className="block mb-3 text-blue-300 font-medium">
                        {selected.shap.verdict}
                      </Typography>

                      {/* Attribution bars */}
                      {Object.entries(selected.shap.attribution)
                        .sort(([, a], [, b]) => b - a)
                        .map(([feature, score]) => (
                          <Box key={feature} className="mb-3">
                            <Box className="flex justify-between mb-1">
                              <Typography variant="caption" className="text-gray-300 capitalize">
                                {feature}
                              </Typography>
                              <Typography variant="caption" className="text-gray-400 font-mono">
                                {(score * 100).toFixed(0)}%
                              </Typography>
                            </Box>
                            <Box className="w-full bg-gray-700 rounded-full h-2">
                              <Box
                                className="rounded-full h-2 transition-all duration-500"
                                sx={{
                                  width: `${Math.min(Math.abs(score) * 100, 100)}%`,
                                  backgroundColor:
                                    score > 0.3 ? '#ef4444' :
                                    score > 0.1 ? '#f97316' : '#3b82f6',
                                }}
                              />
                            </Box>
                          </Box>
                        ))}
                    </Box>
                  ) : (
                    <Box className="p-3 rounded bg-gray-900">
                      <Typography variant="caption" className="text-gray-500 italic">
                        {selected.shap_ready === false
                          ? '⏳ AI is analyzing... check back in ~60 seconds'
                          : 'Analysis not available'}
                      </Typography>
                    </Box>
                  )}
                </Box>

              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelected(null)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </div>
  );
}
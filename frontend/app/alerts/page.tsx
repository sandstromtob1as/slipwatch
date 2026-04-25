'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import {
  Card,
  CardContent,
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
import PhoneIcon from '@mui/icons-material/Phone';
import WarningIcon from '@mui/icons-material/Warning';
import LocationOnIcon from '@mui/icons-material/LocationOn';

interface FallAlert {
  id: string;
  personName: string;
  timestamp: string;
  location: string;
  fallConfidence: number;
  imagePath: string;
  aiExplanation: string;
  emergencyContact: {
    name: string;
    phone: string;
    relation: string;
  };
}

const FallAlertsPage = () => {
  // Sample data - replace with real API data
  const [alerts] = useState<FallAlert[]>([
    {
      id: '1',
      personName: 'Margaret Johnson',
      timestamp: '2025-04-24 14:32:45',
      location: 'Living Room',
      fallConfidence: 0.94,
      imagePath: '/placeholder-fall-1.jpg',
      aiExplanation:
        'High-confidence fall detected. Person is on the ground with rapid downward motion detected. Elderly person appears to need immediate assistance.',
      emergencyContact: {
        name: 'John Johnson',
        phone: '+1 (555) 123-4567',
        relation: 'Son',
      },
    },
    {
      id: '2',
      personName: 'Robert Davis',
      timestamp: '2025-04-24 10:15:22',
      location: 'Bathroom',
      fallConfidence: 0.92,
      imagePath: '/placeholder-fall-2.jpg',
      aiExplanation:
        'Fall detected near bathroom. Person appears to have slipped. Alert sent due to extended time on ground.',
      emergencyContact: {
        name: 'Sarah Davis',
        phone: '+1 (555) 234-5678',
        relation: 'Daughter',
      },
    },
  ]);

  const [selectedAlert, setSelectedAlert] = useState<FallAlert | null>(null);
  const [openDetails, setOpenDetails] = useState(false);

  const handleViewDetails = (alert: FallAlert) => {
    setSelectedAlert(alert);
    setOpenDetails(true);
  };

  const handleCloseDetails = () => {
    setOpenDetails(false);
    setSelectedAlert(null);
  };

  const getConfidenceColor = (confidence: number): 'error' | 'warning' | 'success' => {
    if (confidence >= 0.9) return 'error';
    if (confidence >= 0.7) return 'warning';
    return 'success';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-8">
      <Container maxWidth="lg">
        {/* Header */}
        <Box className="mb-8">
          <Typography
            variant="h2"
            className="font-bold text-white mb-2 flex items-center gap-3"
          >
            Overview
          </Typography>
          <Typography variant="body1" className="text-gray-300">
            Respond to active fall alerts and review detailed incident reports. Ensure the safety of your loved ones with real-time monitoring and AI-powered insights.
          </Typography>
        </Box>

        {/* Alerts Grid */}
        {alerts.length > 0 ? (
          <Box className="flex flex-col gap-6">
            {alerts.map((alert) => (
              <Card key={alert.id} sx={{ backgroundColor: '#1f2937', borderColor: '#374151' }} className="h-full shadow-lg hover:shadow-xl transition-shadow duration-300 flex flex-row border border-gray-700">
                  {/* Image Area */}
                  <CardMedia
                    component="div"
                    className="relative flex-grow h-auto bg-gray-700 flex items-center justify-center overflow-hidden"
                  >
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-700 to-gray-600">
                      <span className="text-gray-400 text-sm">
                        Fall Detection Camera Image
                      </span>
                    </div>
                    {/* Confidence Badge */}
                    <Box className="absolute top-3 right-3">
                      <Chip
                        label={`Confidence: ${(alert.fallConfidence * 100).toFixed(0)}%`}
                        color={getConfidenceColor(alert.fallConfidence)}
                        variant="filled"
                        size="small"
                      />
                    </Box>
                    {/* Alert Status Badge */}
                    <Box className="absolute top-3 left-3">
                      <Chip
                        icon={<WarningIcon />}
                        label="ACTIVE ALERT"
                        color="error"
                        variant="filled"
                        size="small"
                      />
                    </Box>
                  </CardMedia>

                  <Box className="flex flex-col flex-grow max-w-md ml-auto pr-6">
                  <CardHeader
                    title={
                      <Typography variant="h6" className="font-bold text-white">
                        {alert.personName}
                      </Typography>
                    }
                    subheader={
                      <Box className="flex flex-col gap-1 mt-1">
                        <Typography variant="caption" className="text-gray-400">
                          {alert.timestamp}
                        </Typography>
                        <Typography
                          variant="caption"
                          className="flex items-center gap-1 text-gray-300"
                        >
                          <LocationOnIcon fontSize="small" />
                          {alert.location}
                        </Typography>
                      </Box>
                    }
                  />

                  <CardContent className="flex-grow">
                    {/* AI Explanation */}
                    <Box className="mb-4">
                      <Typography variant="subtitle2" className="font-semibold text-gray-100 mb-2">
                        AI Analysis
                      </Typography>
                      <Typography
                        variant="body2"
                        className="text-gray-300 p-3 bg-blue-900 rounded-md border-l-4 border-blue-500"
                      >
                        {alert.aiExplanation}
                      </Typography>
                    </Box>

                    {/* Emergency Contact */}
                    <Box className="bg-red-900 p-3 rounded-md border-l-4 border-red-500">
                      <Typography
                        variant="subtitle2"
                        className="font-semibold text-gray-100 mb-2"
                      >
                        Emergency Contact
                      </Typography>
                      <Typography variant="body2" className="text-gray-100 font-medium">
                        {alert.emergencyContact.name}
                      </Typography>
                      <Typography variant="caption" className="text-gray-400">
                        {alert.emergencyContact.relation}
                      </Typography>
                      <Box className="mt-2 flex items-center gap-2">
                        <PhoneIcon fontSize="small" className="text-red-400" />
                        <Typography
                          variant="body2"
                          className="font-mono text-red-400 font-semibold"
                        >
                          {alert.emergencyContact.phone}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>

                  {/* Actions */}
                  <Box className="p-4 pt-0 flex gap-2">
                    <Button
                      variant="contained"
                      color="error"
                      size="small"
                      startIcon={<PhoneIcon />}
                      fullWidth
                    >
                      Call Now
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleViewDetails(alert)}
                      fullWidth
                    >
                      Details
                    </Button>
                  </Box>
                  </Box>
                </Card>
            ))}
          </Box>
        ) : (
          <Card sx={{ backgroundColor: '#1f2937' }} className="p-8 text-center border border-gray-700">
            <Typography variant="h6" className="text-gray-400">
              No active fall alerts
            </Typography>
          </Card>
        )}
      </Container>

      {/* Details Dialog */}
      <Dialog
        open={openDetails}
        onClose={handleCloseDetails}
        maxWidth="sm"
        fullWidth
        sx={{
          '& .MuiDialog-paper': {
            backgroundColor: '#1f2937',
            color: '#fff'
          }
        }}
      >
        {selectedAlert && (
          <>
            <DialogTitle className="bg-red-900 border-b-2 border-red-500">
              <Box className="flex items-center gap-2">
                <WarningIcon className="text-red-400" />
                <Typography variant="h6" className="font-bold text-white">
                  {selectedAlert.personName} - Detailed Report
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent className="mt-4 bg-gray-800">
              <Box className="flex flex-col gap-4">
                <Box>
                  <Typography variant="subtitle2" className="font-semibold mb-1 text-gray-100">
                    Incident Time
                  </Typography>
                  <Typography variant="body2" className="text-gray-300">
                    {selectedAlert.timestamp}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" className="font-semibold mb-1 text-gray-100">
                    Location
                  </Typography>
                  <Typography variant="body2" className="text-gray-300">
                    {selectedAlert.location}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" className="font-semibold mb-1 text-gray-100">
                    Fall Confidence Score
                  </Typography>
                  <Chip
                    label={`${(selectedAlert.fallConfidence * 100).toFixed(1)}%`}
                    color={getConfidenceColor(selectedAlert.fallConfidence)}
                    className="mb-2"
                  />
                </Box>

                <Box>
                  <Typography variant="subtitle2" className="font-semibold mb-1 text-gray-100">
                    AI Analysis Details
                  </Typography>
                  <Typography
                    variant="body2"
                    className="text-gray-300 p-2 bg-blue-900 rounded"
                  >
                    {selectedAlert.aiExplanation}
                  </Typography>
                </Box>

                <Box className="bg-red-900 p-3 rounded-md">
                  <Typography variant="subtitle2" className="font-semibold mb-2 text-gray-100">
                    Emergency Contact
                  </Typography>
                  <Typography variant="body2" className="font-medium text-gray-100">
                    {selectedAlert.emergencyContact.name}
                  </Typography>
                  <Typography variant="caption" className="text-gray-400">
                    {selectedAlert.emergencyContact.relation}
                  </Typography>
                  <Typography
                    variant="body2"
                    className="font-mono text-red-400 font-semibold mt-1"
                  >
                    {selectedAlert.emergencyContact.phone}
                  </Typography>
                </Box>
              </Box>
            </DialogContent>
            <DialogActions className="border-t pt-4">
              <Button onClick={handleCloseDetails}>Close</Button>
              <Button variant="contained" color="error" startIcon={<PhoneIcon />}>
                Call Emergency Contact
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </div>
  );
};

export default FallAlertsPage;

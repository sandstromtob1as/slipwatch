'use client';

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Container,
  Grid,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CardHeader,
  CardMedia,
} from '@mui/material';
import {
  Warning,
  Dashboard,
  ListAlt,
  Settings,
  CheckCircle,
} from '@mui/icons-material';
import WarningIcon from '@mui/icons-material/Warning';
import PeopleIcon from '@mui/icons-material/People';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SecurityIcon from '@mui/icons-material/Security';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import PhoneIcon from '@mui/icons-material/Phone';

interface FallAlert {
  id: string;
  personName: string;
  timestamp: string;
  location: string;
  fallConfidence: number;
  aiExplanation: string;
  emergencyContact: {
    name: string;
    phone: string;
    relation: string;
  };
  isAlert: boolean;
}

export default function Home() {
  const [alerts] = useState<FallAlert[]>([
    {
      id: '1',
      personName: 'Margaret Johnson',
      timestamp: '2025-04-24 14:32:45',
      location: 'Living Room',
      fallConfidence: 0.94,
      aiExplanation:
        'High-confidence fall detected. Person is on the ground with rapid downward motion detected. Elderly person appears to need immediate assistance.',
      emergencyContact: {
        name: 'John Johnson',
        phone: '+1 (555) 123-4567',
        relation: 'Son',
      },
      isAlert: true,
    },
    {
      id: '2',
      personName: 'Robert Davis',
      timestamp: '2025-04-24 10:15:22',
      location: 'Bathroom',
      fallConfidence: 0.6,
      aiExplanation:
        'Fall detected near bathroom. Person appears to have slipped. Alert sent due to extended time on ground.',
      emergencyContact: {
        name: 'Sarah Davis',
        phone: '+1 (555) 234-5678',
        relation: 'Daughter',
      },
      isAlert: false,
    },
  ]);

  const [selectedAlert, setSelectedAlert] = useState<FallAlert | null>(null);
  const [openDetails, setOpenDetails] = useState(false);

  const getConfidenceColor = (confidence: number): 'error' | 'warning' | 'success' => {
    if (confidence >= 0.9) return 'error';
    if (confidence >= 0.7) return 'warning';
    return 'success';
  };

  const handleViewDetails = (alert: FallAlert) => {
    setSelectedAlert(alert);
    setOpenDetails(true);
  };

  const handleCloseDetails = () => {
    setOpenDetails(false);
    setSelectedAlert(null);
  };

  return (
    <div className="min-h-screen py-8">
      <Container maxWidth="lg">
        <Box className="mb-8">
          <Typography
            variant="h2"
            className="font-bold text-white mb-2 flex items-center gap-3"
          >
            Overview
          </Typography>
          <Typography variant="body1" className="text-gray-300">
            Active alerts are displayed here with AI analysis and emergency contact information so you can respond quickly.
          </Typography>
        </Box>

        {alerts.length > 0 ? (
          <Box className="flex flex-col gap-6">
            {alerts.map((alert) => (
              <Card key={alert.id} sx={{ backgroundColor: '#1f2937', borderColor: '#374151' }} className="border border-gray-700 shadow-lg transition-shadow duration-300">
                <Box className={alert.isAlert ? "lg:flex" : ""}>
                  {alert.isAlert && (
                  <CardMedia
                    component="div"
                    className="lg:w-2/3 h-52 lg:h-auto bg-gray-700 flex items-center justify-center"
                  >
                    <Typography className="text-gray-400">Camera preview image</Typography>
                  </CardMedia>
                  )}
                  <Box className={`p-6 ${alert.isAlert ? "lg:w-1/3" : "w-full"}`}>
                    <CardHeader
                      title={
                        <div className="flex items-center gap-2">
                          <Typography variant="h5" className="font-bold text-white">
                            {alert.personName}
                          </Typography>
                          {alert.isAlert && (
                          <Warning className="text-red-500" fontSize="medium" />
                          )}
                        </div>
                      }
                      action={
                        !alert.isAlert && (
                         <Box className="flex justify-end items-center gap-2 mt-4">
                          <CheckCircle className="text-green-400" fontSize="small" />
                        </Box>
                        )
                      }
                      
                      subheader={
                        alert.isAlert ? (
                          <Box className="flex flex-col gap-1 mt-1">
                            <Typography variant="caption" className="text-gray-400">
                              {alert.timestamp}
                            </Typography>
                            <Typography variant="caption" className="flex items-center gap-1 text-gray-300">
                              <LocationOnIcon fontSize="small" />
                              {alert.location}
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="caption" className="text-green-400 mt-1">
                            No active alert • Monitoring
                          </Typography>
                        )
                      }
                      
                    />
                    {alert.isAlert && (
                    <Box className="mb-4">
                      <Typography variant="subtitle2" className="font-semibold text-gray-100 mb-2">
                        AI Explanation
                      </Typography>
                      <Typography variant="body2" className="text-gray-300 p-3 rounded-md bg-blue-900 border-l-4 border-blue-500">
                        {alert.aiExplanation}
                      </Typography>
                    </Box>
                    )}
                    {alert.isAlert && (
                    <Box className="bg-red-900 p-4 rounded-md border-l-4 border-red-500 mb-4">
                      <Typography variant="subtitle2" className="font-semibold text-gray-100 mb-2">
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
                        <Typography variant="body2" className="font-mono text-red-400 font-semibold">
                          {alert.emergencyContact.phone}
                        </Typography>
                      </Box>
                    </Box>
                    )}
                    {alert.isAlert && (
                    <Box className="flex flex-col gap-3 sm:flex-row">
                      <Button variant="contained" color="error" fullWidth startIcon={<PhoneIcon />}>
                        Call Now
                      </Button>
                      <Button variant="outlined" fullWidth onClick={() => handleViewDetails(alert)}>
                        Details
                      </Button>
                    </Box>
                    )}
                    
                  </Box>
                </Box>
              </Card>
            ))}
          </Box>
        ) : (
          <Card sx={{ backgroundColor: '#1f2937' }} className="p-8 text-center border border-gray-700">
            <Typography variant="h6" className="text-gray-400">
              No monitored persons added to the overview.
            </Typography>
          </Card>
        )}
      </Container>

      <Dialog
        open={openDetails}
        onClose={handleCloseDetails}
        maxWidth="sm"
        fullWidth
        sx={{
          '& .MuiDialog-paper': {
            backgroundColor: '#1f2937',
            color: '#fff',
          },
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
                  <Typography variant="body2" className="text-gray-300 p-2 rounded bg-blue-900">
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
                  <Typography variant="body2" className="font-mono text-red-400 font-semibold mt-1">
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
}

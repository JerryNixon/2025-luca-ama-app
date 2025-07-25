// Simple Test Component to verify our integration works

import React from 'react';

export default function SimpleTest() {
  console.log('🧪 SimpleTest component is rendering!');
  
  return (
    <div style={{
      backgroundColor: 'lime',
      color: 'black',
      padding: '20px',
      margin: '10px',
      border: '3px solid red',
      fontWeight: 'bold'
    }}>
      ✅ SIMPLE TEST COMPONENT IS WORKING!
      <br />
      If you see this, React rendering is working correctly.
    </div>
  );
}

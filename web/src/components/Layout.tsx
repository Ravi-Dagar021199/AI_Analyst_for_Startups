import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Link, Outlet } from 'react-router-dom';
import { auth } from '../firebase';

export default function Layout() {
  return (
    <div>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>AI Analyst</Link>
          </Typography>
          <Button color="inherit" component={Link} to="/upload">Upload</Button>
          <Button color="inherit" component={Link} to="/dashboard">Reports</Button>
          <Button color="inherit" onClick={() => auth.signOut()}>Sign Out</Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>
        <Outlet />
      </Container>
    </div>
  );
}
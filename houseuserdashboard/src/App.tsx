import RouteList from './Routes';
import './assets/css/argon-dashboard.css';
import './assets/css/nucleo-icons.css';
import './assets/css/fa-main.css';
import './assets/css/fa-v4-font-face.css';
import './assets/css/fa-v4-shims.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';


function App() {
  return (
    <div className="App">
      <RouteList />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </div>
  );
}

export default App;

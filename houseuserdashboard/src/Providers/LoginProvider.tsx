import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Outlet, useNavigate } from 'react-router-dom'
import { RootState } from '../Stores/reducers'

const LoginProvider = () => {
  let navigate = useNavigate()
  let User = useSelector((state: RootState) => state.user)

  useEffect(() => {
    let token = localStorage.getItem('access_token')
    if (token) {
      navigate('/admin/dashboard')
    }
  }, [User.data, User.error])
  return <Outlet />
}

export default LoginProvider

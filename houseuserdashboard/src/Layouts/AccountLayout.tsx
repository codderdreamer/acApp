import { useTranslation } from 'react-i18next'
import { Outlet } from 'react-router-dom'

const AccountLayout = () => {
  const { t, i18n } = useTranslation()

  function ChangeLanguage(lang: string) {
    i18n.changeLanguage(lang)
    localStorage.setItem('lang', lang)
  }

  return (
    <>
      <div className="page-header min-vh-100">
        <div className="container">
          <div className="row">
            <div className="col-sm-12 col-md-6">
              <Outlet />
              <div
                className="col-xl-8 col-lg-12 col-md-12 d-flex flex-column"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <select
                  className="form-control text-center border"
                  style={{
                    background: 'transparent',
                    border: 'none',
                    width: '200px'
                  }}
                  defaultValue={localStorage.getItem('lang') ?? 'en'}
                  onChange={(e) => ChangeLanguage(e.target.value)}
                >
                  <option value="tr">Türkçe</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>
            <div className="col-6 d-lg-flex d-none h-100 my-auto pe-0 position-absolute top-0 end-0 text-center justify-content-center flex-column">
              <div
                className="position-relative bg-gradient-primary h-100 m-3 px-7 border-radius-lg d-flex flex-column justify-content-center overflow-hidden"
                style={{
                  backgroundImage: 'url( "https://images.pexels.com/photos/9799996/pexels-photo-9799996.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")',
                  backgroundSize: 'cover'
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default AccountLayout

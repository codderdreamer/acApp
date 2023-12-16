import { useState } from 'react'
import { ChangePasswordService } from './services'
import { toast } from 'react-toastify'
import { useTranslation } from 'react-i18next'
import PasswordInput from '../../Components/PasswordInput'

const Profile = () => {
  const [Password, setPassword] = useState('')
  const [NewPassword, setNewPassword] = useState('')
  const [NewPasswordConfirm, setNewPasswordConfirm] = useState('')
  const { t } = useTranslation()

  async function ChangePassword() {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$/
    if (!regex.test(NewPassword)) {
      toast.error(t('password-requirements'))
      return
    }

    if (NewPassword !== NewPasswordConfirm) {
      toast.error(t('new-password-not-match'))
      return
    }

    try {
      await ChangePasswordService({ old_password: Password, new_password: NewPassword })
      toast.success(t('change-password-success'))
    } catch (error: any) {
      if (error.response.data.message) {
        toast.error(error.response.data.message)
        return
      }

      toast.error(t('change-password-failed'))
    }
  }

  return (
    <>
      <div className="card shadow-lg mx-4 card-profile-bottom" style={{ marginTop: '12rem' }}>
        <div className="card-body p-3">
          <div className="row gx-4">
            <div className="col-auto">
              <div className="avatar avatar-xl position-relative">
                <img src="../assets/img/user.png" />
              </div>
            </div>
            <div className="col-auto my-auto">
              <div className="h-100">
                <h5 className="mb-1">{t('profile')}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container-fluid py-4">
        <div className="row mb-3">
          <div className="col-12">
            <div className="card">
              <div className="card-body">
                <div className="row mb-3">
                  <label>{t('change-password')}</label>
                  <div className="col-lg-6 col-sm-12">
                    <PasswordInput onChange={(value: string) => setPassword(value)} title={t('old-password')} placeholder={t('old-password')} />
                  </div>
                  <div className="col-lg-6 col-sm-12">
                    <PasswordInput onChange={(value: string) => setNewPassword(value)} title={t('new-password')} placeholder={t('new-password')} />
                  </div>
                  <div className="col-lg-6 col-sm-12">
                    <PasswordInput onChange={(value: string) => setNewPasswordConfirm(value)} title={t('new-password-confirm')} placeholder={t('new-password-confirm')} />
                  </div>
                  <div className="col-lg-6 col-sm-12">
                    <label></label>
                    <p className="text-sm">{t('password-requirements')}</p>
                  </div>
                  <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0 mt-4">
                    <button className="btn btn-primary btn-sm mb-0" type="button" name="button" onClick={ChangePassword}>
                      {t('submit')}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Profile

import { useState } from 'react';

export const useAuthDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState<'login' | 'register'>('login');

  const openLogin = () => {
    setMode('login');
    setIsOpen(true);
  };

  const openRegister = () => {
    setMode('register');
    setIsOpen(true);
  };

  const close = () => {
    setIsOpen(false);
  };

  return {
    isOpen,
    mode,
    openLogin,
    openRegister,
    close
  };
};

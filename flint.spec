%define name		flint
%define flintdir	%{_datadir}/%{name}
%define libmajor	1
%define libname		%mklibname %{name} %{libmajor}

Name:		%{name}
Group:		Sciences/Mathematics
License:	GPL
Summary:	FLINT - Fast Library for Number Theory
Version:	1.5.0
Release:	7
Source:		http://www.flintlib.org/flint-%{version}.tar.gz
URL:		http://www.flintlib.org/

BuildRequires:	gmp-devel
BuildRequires:	ntl-devel
BuildRequires:	python
BuildRequires:	zn_poly-devel

Requires:	pari
Requires:	python-matplotlib

# Based on sagemath & debian package
Patch0:		flint-1.5.0-soname.patch

# Link applications with the generated dynamic library instead of the .o files
Patch1:		flint-1.5.0-dynlink.patch

# Link ntl interface in libflint.so; this interface is required by
# sage python modules.
Patch2:		flint-1.5.0-ntl.patch

Patch3:		flint-1.5.0-zn_poly.patch

%description
FLINT - Fast Library for Number Theory. FLINT is a C library for
doing number theory, written by William Hart and David Harvey.

%package	-n %{libname}
Group:		System/Libraries
Summary:	Shared FLINT library
Provides:	lib%{name} = %{version}-%{release}

%description	-n %{libname}
This package contains the shared FLINT libraries.

%package	-n lib%{name}-devel
Group:		Development/C
Summary:	FLINT Development files
Requires:	lib%{name} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description	-n lib%{name}-devel
This package contains the FLINT development headers and libraries.

%prep
%setup -q

%patch0	-p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
rm -fr zn_poly

%build
make						\
	LIBDIR=%{_libdir}			\
	INCLUDEDIR=%{_includedir}		\
	DOCDIR=%{_docdir}/%{name}-%{version}	\
	FLINT_NTL_LIB_DIR=%{_libdir}		\
	FLINT_GMP_LIB_DIR=%{_libdir}		\
	FLINT_GMP_INCLUDE_DIR=%{_includedir}	\
	FLINT_LIB=libflint.so			\
	FLINT_VERSION=%{version}		\
	FLINT_TUNE=-fPIC			\
	library all

%install
mkdir -p %{buildroot}/%{flintdir}/bin
cp -fa `find . -maxdepth 1 -mindepth 1 -type f -executable | grep -v libflint` \
	 %{buildroot}/%{flintdir}/bin

mkdir -p %{buildroot}/%{_libdir}
cp -fa libflint* %{buildroot}/%{_libdir}

perl -pi -e 's|(#include "zn_poly/)src/(zn_poly.h")|$1$2|;' *.h
mkdir -p %{buildroot}/%{_includedir}/%{name}
cp -fa *.h %{buildroot}/%{_includedir}/%{name}

# sagemath expects it this way
ln -sf %{_includedir}/%{name} %{buildroot}%{_includedir}/FLINT

cp -far graphing  %{buildroot}/%{flintdir}
cp -far pari-profiles %{buildroot}/%{flintdir}

ln -sf %{_docdir}/%{name} %{buildroot}%{flintdir}/doc

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%dir %{flintdir}
%{flintdir}/*
%doc doc/*

%files		-n %{libname}
%defattr(-,root,root)
%{_libdir}/libflint.so.*

%files		-n lib%{name}-devel
%defattr(-,root,root)
%{_libdir}/libflint.so
%{_includedir}/FLINT
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%doc CHANGES.txt


%changelog
* Tue Mar 08 2011 Paulo Andrade <pcpa@mandriva.com.br> 1.5.0-6mdv2011.0
+ Revision: 642764
- Rebuild using system dynamically linked zn_poly

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 1.5.0-5mdv2011.0
+ Revision: 610713
- rebuild

* Wed Feb 10 2010 Funda Wang <fwang@mandriva.org> 1.5.0-4mdv2010.1
+ Revision: 503581
- rebuild for new gmp

* Sat Jan 23 2010 Paulo Andrade <pcpa@mandriva.com.br> 1.5.0-3mdv2010.1
+ Revision: 495127
+ rebuild (emptylog)

* Wed Nov 25 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.5.0-2mdv2010.1
+ Revision: 470132
+ rebuild (emptylog)

* Wed Nov 25 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.5.0-1mdv2010.1
+ Revision: 470126
- Update to latest upstream release 1.5.0

* Mon Jul 20 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.3.0-1mdv2010.0
+ Revision: 398231
- Update to newer upstream release 1.3.0.

* Tue Jun 16 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.0.21-6mdv2010.0
+ Revision: 386229
+ rebuild (emptylog)

* Mon May 18 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.0.21-5mdv2010.0
+ Revision: 377314
+ rebuild (emptylog)

* Mon May 18 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.0.21-4mdv2010.0
+ Revision: 377282
+ rebuild (emptylog)

* Fri May 08 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.0.21-3mdv2010.0
+ Revision: 373518
- Link NTL-interface.o in libflint, as those symbols are required by sagemath.

* Tue Mar 10 2009 Paulo Andrade <pcpa@mandriva.com.br> 1.0.21-1mdv2009.1
+ Revision: 353511
- Initial import of flint 1.0.21.
  FLINT is a C library for doing number theory
  http://www.flintlib.org/
- flint


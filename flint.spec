%define name		flint
%define flintdir	%{_datadir}/%{name}
%define libmajor	1
%define libname		%mklibname %{name} %{libmajor}

Name:		%{name}
Group:		Sciences/Mathematics
License:	GPL
Summary:	FLINT is a C library for doing number theory
Version:	1.0.21
Release:	%mkrel 1
Source:		http://www.flintlib.org/flint-1.0.21.tar.gz
URL:		http://www.flintlib.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	libgmp-devel
BuildRequires:	ntl-devel
BuildRequires:	python
Requires:	pari
Requires:	python-matplotlib

# Based on sagemath & debian package
Patch0:		flint-1.0.21-soname.patch

# Link applications with the generated dynamic library instead of the .o files
Patch1:		flint-1.0.21-dynlink.patch

%description
FLINT is a C library for doing number theory,
written by William Hart and David Harvey.

%package	-n %{libname}
Group:		System/Libraries
Summary:	Shared FLINT library
Provides:	lib%{name} = %{version}-%{release}

%description	-n %{libname}
This package contains the shared FLINT libraries.

%package	-n lib%{name}-devel
Group:		Development/C
Summary:	FLINT Development files
Provides:	lib%{name} = %{version}-%{release}

%description	-n lib%{name}-devel
This package contains the FLINT development headers and libraries.

%prep
%setup -q

%patch0	-p1
%patch1 -p1

%build
make						\
	LIBDIR=%{_libdir}			\
	INCLUDEDIR=%{_includedir}		\
	DOCDIR=%{_docdir}/%{name}-%{version}	\
	FLINT_GMP_LIB_DIR=%{_libdir}		\
	FLINT_GMP_INCLUDE_DIR=%{_includedir}	\
	FLINT_LIB=libflint.so			\
	FLINT_VERSION=%{version}		\
	library all

%install
mkdir -p %{buildroot}/%{flintdir}/bin
cp -fa `find . -maxdepth 1 -mindepth 1 -type f -executable | grep -v libflint` \
	 %{buildroot}/%{flintdir}/bin

mkdir -p %{buildroot}/%{_libdir}
cp -fa libflint* %{buildroot}/%{_libdir}

mkdir -p %{buildroot}/%{_includedir}/%{name}
cp -fa *.h %{buildroot}/%{_includedir}/%{name}

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
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%doc CHANGES.txt
%define flintdir	%{_datadir}/flint
%define old_libname	%mklibname flint 1

Name:           flint
Version:        1.6
Release:        1%{?dist}
Summary:        Fast Library for Number Theory
License:        GPLv2+
URL:            http://www.flintlib.org/
Source0:        http://www.flintlib.org/flint-%{version}.tgz
Source1:        %{name}.rpmlintrc
# Build (not really) a static lib (since upstream doesn't keep track of
# compatible interfaces a soname really makes no sense
Patch0:         flint-1.2.0-add-static-lib.diff
# Use the system zn_poly instead of building the sources
Patch1:         flint-1.6-use-system-zn_poly.patch
# Fix some variable redefinitions; gcc 4.6 errors out otherwise
Patch2:         flint-1.6-redef.patch
# Fix some compiler warnings that indicate possible runtime problems
Patch3:         flint-1.6-warning.patch
# Link  with NTL
Patch4:         flint-1.6-ntl.patch

BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  ntl-devel
BuildRequires:  zn_poly-devel
BuildRequires:  texlive
%rename %{old_libname}
%global sover %(echo %{version} | cut -d. -f 1)

%description
FLINT is a C library for doing number theory, written by William Hart
and David Harvey.

%package	devel
Summary:	FLINT Development files
Requires:	%{name} = %{EVRD}
%rename libflint-devel

%description	devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q
%patch0
%patch1
%patch2
%patch3
%patch4 -p1

# Make sure we don't accidentally use the included zn_poly sources
rm -fr zn_poly

# Add an soname for the shared library and set other values
sed -e 's|^LIBDIR=.*$|LIBDIR=%{_libdir}|'                        \
    -e 's|^INCLUDEDIR=.*$|INCLUDEDIR=%{_includedir}|'            \
    -e 's|^DOCDIR=.*$|DOCDIR=%{_docdir}|'                        \
    -e 's|^CFLAGS =.*$|CFLAGS = $(INCS) %{optflags} -fPIC|'      \
    -e 's|^CFLAGS2 =.*$|CFLAGS2 = $(INCS) %{optflags} -fopenmp -fPIC|' \
    -e "s|-shared|-shared -Wl,-h,libflint.so.%{sover}|"          \
    -e 's|mp_lprels\.o \$(FLINTOBJ)$|mp_lprels.o libflint.so|'   \
    -e 's|mp_lprels\.o \$(FLINTOBJ)|mp_lprels.o -L. -lflint|'    \
    -i makefile

# Fix end-of-line encodings
sed 's/\r//' CHANGES.txt > CHANGES
touch -r CHANGES.txt CHANGES
mv -f CHANGES CHANGES.txt

%build
make %{?_smp_mflags} MAKECMDGOALS=library \
	FLINT_GMP_LIB_DIR=%{_libdir}	\
	FLINT_NTL_LIB_DIR=%{_libdir}	\
	FLINT_TUNE=-fPIC
rm -f *.o
make FLINT_GMP_LIB_DIR=%{_libdir} FLINT_NTL_LIB_DIR=%{_libdir}

# Build the documentation
cd doc
pdflatex %{name}-%{version}.tex
pdflatex %{name}-%{version}.tex

%install
# generated in build: mpQS libflint.so
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}
install -d -m 755 $RPM_BUILD_ROOT%{_bindir}
install -p -m 755 mpQS $RPM_BUILD_ROOT%{_bindir}/
# install the headers somehow...
install -d -m 755 $RPM_BUILD_ROOT%{_includedir}/%{name}
for header in *.h; do
  install -p -m 644 $header $RPM_BUILD_ROOT%{_includedir}/%{name}/
done

install -p -m 755 libflint.so $RPM_BUILD_ROOT%{_libdir}/libflint.so.%{sover}
pushd $RPM_BUILD_ROOT%{_libdir}/
  ln -s libflint.so.%{sover} libflint.so
popd

# add symlink FLINT -> flint | sagemath wants it that way
pushd $RPM_BUILD_ROOT%{_includedir}
    ln -s flint FLINT
popd

%files
%doc CHANGES.txt gpl-2.0.txt doc/%{name}-%{version}.pdf
%{_bindir}/mpQS
%{_libdir}/libflint.so.%{sover}

%files devel
%{_includedir}/flint
%{_includedir}/FLINT
%{_libdir}/libflint.so

/*
LICENSE: the software is a modification from Python 2.4.3's socketmodule.c/socketmodule.h
*/
/*
irsocket -- IrDA networking interface

irda_socket = _irsocket.socket()
irda_socket.getsockopt()
irda_socket.connect()
irda_socket.close()
irda_socket.sendall()
irda_socket.recv()
irda_socket.settimeout()
irda_socket.gettimeout()
*/

#include <sys/types.h>
#include <Python.h>

#if defined(MS_WINDOWS)
#include <winsock2.h>
#include <ws2tcpip.h>
#include <af_irda.h>
#define sockaddr_irda _SOCKADDR_IRDA
#else
#include <linux/types.h>
#include <linux/irda.h>
#endif

#if defined(MS_WINDOWS)
#define SOCKETCLOSE closesocket
#endif

#ifndef SOCKETCLOSE
#define SOCKETCLOSE close
#endif

#define IS_SELECTABLE(s) 1

typedef struct {
    PyObject_HEAD
    int sock_fd;
    double sock_timeout;
    struct sockaddr_irda ir;
} PyIrSockObject;

/* Function to perform the setting of socket blocking mode
   internally. block = (1 | 0). */
static int
internal_setblocking(PyIrSockObject *s, int block)
{
#ifndef RISCOS
#ifndef MS_WINDOWS
    int delay_flag;
#endif
#endif

    Py_BEGIN_ALLOW_THREADS
#ifdef __BEOS__
    block = !block;
    setsockopt(s->sock_fd, SOL_SOCKET, SO_NONBLOCK,
           (void *)(&block), sizeof(int));
#else
#ifndef RISCOS
#ifndef MS_WINDOWS
#if defined(PYOS_OS2) && !defined(PYCC_GCC)
    block = !block;
    ioctl(s->sock_fd, FIONBIO, (caddr_t)&block, sizeof(block));
#elif defined(__VMS)
    block = !block;
    ioctl(s->sock_fd, FIONBIO, (char *)&block);
#else  /* !PYOS_OS2 && !_VMS */
    delay_flag = fcntl(s->sock_fd, F_GETFL, 0);
    if (block)
        delay_flag &= (~O_NONBLOCK);
    else
        delay_flag |= O_NONBLOCK;
    fcntl(s->sock_fd, F_SETFL, delay_flag);
#endif /* !PYOS_OS2 */
#else /* MS_WINDOWS */
    block = !block;
    ioctlsocket(s->sock_fd, FIONBIO, (u_long*)&block);
#endif /* MS_WINDOWS */
#else /* RISCOS */
    block = !block;
    socketioctl(s->sock_fd, FIONBIO, (u_long*)&block);
#endif /* RISCOS */
#endif /* __BEOS__ */
    Py_END_ALLOW_THREADS

    /* Since these don't return anything */
    return 1;
}

/* Do a select() on the socket, if necessary (sock_timeout > 0).
   The argument writing indicates the direction.
   This does not raise an exception; we'll let our caller do that
   after they've reacquired the interpreter lock.
   Returns 1 on timeout, 0 otherwise. */
static int
internal_select(PyIrSockObject *s, int writing)
{
    fd_set fds;
    struct timeval tv;
    int n;

    /* Nothing to do unless we're in timeout mode (not non-blocking) */
    if (s->sock_timeout <= 0.0)
        return 0;

    /* Guard against closed socket */
    if (s->sock_fd < 0)
        return 0;

    /* Construct the arguments to select */
    tv.tv_sec = (int)s->sock_timeout;
    tv.tv_usec = (int)((s->sock_timeout - tv.tv_sec) * 1e6);
    FD_ZERO(&fds);
    FD_SET(s->sock_fd, &fds);

    /* See if the socket is ready */
    if (writing)
        n = select(s->sock_fd+1, NULL, &fds, NULL, &tv);
    else
        n = select(s->sock_fd+1, &fds, NULL, NULL, &tv);
    if (n == 0)
        return 1;
    return 0;
}


static int
internal_connect(PyIrSockObject *s, struct sockaddr *addr, int addrlen,
         int *timeoutp)
{
    int res, timeout;

    timeout = 0;
    res = connect(s->sock_fd, addr, addrlen);

#ifdef MS_WINDOWS

    if (s->sock_timeout > 0.0) {
        if (res < 0 && WSAGetLastError() == WSAEWOULDBLOCK &&
            IS_SELECTABLE(s)) {
            /* This is a mess.  Best solution: trust select */
            fd_set fds;
            fd_set fds_exc;
            struct timeval tv;
            tv.tv_sec = (int)s->sock_timeout;
            tv.tv_usec = (int)((s->sock_timeout - tv.tv_sec) * 1e6);
            FD_ZERO(&fds);
            FD_SET(s->sock_fd, &fds);
            FD_ZERO(&fds_exc);
            FD_SET(s->sock_fd, &fds_exc);
            res = select(s->sock_fd+1, NULL, &fds, &fds_exc, &tv);
            if (res == 0) {
                res = WSAEWOULDBLOCK;
                timeout = 1;
            } else if (res > 0) {
                if (FD_ISSET(s->sock_fd, &fds))
                    /* The socket is in the writeable set - this
                       means connected */
                    res = 0;
                else {
                    /* As per MS docs, we need to call getsockopt()
                       to get the underlying error */
                    int res_size = sizeof res;
                    /* It must be in the exception set */
                    assert(FD_ISSET(s->sock_fd, &fds_exc));
                    if (0 == getsockopt(s->sock_fd, SOL_SOCKET, SO_ERROR,
                                        (char *)&res, &res_size))
                        /* getsockopt also clears WSAGetLastError,
                           so reset it back. */
                        WSASetLastError(res);
                    else
                        res = WSAGetLastError();
                }
            }
            /* else if (res < 0) an error occurred */
        }
    }

    if (res < 0)
        res = WSAGetLastError();

#else

    if (s->sock_timeout > 0.0) {
        if (res < 0 && errno == EINPROGRESS && IS_SELECTABLE(s)) {
            timeout = internal_select(s, 1);
            res = connect(s->sock_fd, addr, addrlen);
            if (res < 0 && errno == EISCONN)
                res = 0;
        }
    }

    if (res < 0)
        res = errno;

#endif
    *timeoutp = timeout;

    return res;
}



PyDoc_STRVAR(irsock_doc,
"irsocket -- IrDA networking interface");

static void
irsock_dealloc(PyIrSockObject *s)
{
    if (s->sock_fd != -1) {
        SOCKETCLOSE(s->sock_fd);
    }
    s->ob_type->tp_free((PyObject*)s);
}

static PyObject *
irsock_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyIrSockObject *s;
    s = (PyIrSockObject *)type->tp_alloc(type, 0);
    if (s != NULL) {
        s->sock_fd = -1;
        s->sock_timeout = -1.0;
    }
    return (PyObject *)s;
}

static int
irsock_init(PyIrSockObject *self, PyObject *args, PyObject *kwds)
{
    int fd;

    Py_BEGIN_ALLOW_THREADS
    fd = socket(AF_IRDA, SOCK_STREAM, 0);
    Py_END_ALLOW_THREADS

#ifdef MS_WINDOWS
    if (fd == INVALID_SOCKET) {
#else
    if (fd < 0) {
#endif
        return -1;
    }
    self->sock_fd = fd;
    self->sock_timeout = -1.0;
    return 0;
}

static PyObject *
irsock_getsockopt(PyIrSockObject *s, PyObject *args)
{
    int level;
    int optname;
    int res;
    PyObject *buf;
    socklen_t buflen = 0;
    if (!PyArg_ParseTuple(args, "ii|i:getsockopt", &level, &optname, &buflen)) {
        return NULL;
    }
    if (buflen <= 0 || buflen > 1024) {
        return NULL;
    }
    buf = PyString_FromStringAndSize((char *)NULL, buflen);
    if (buf == NULL) {
        return NULL;
    }
    res = getsockopt(s->sock_fd, level, optname, (void *)PyString_AS_STRING(buf), &buflen);
    if (res < 0) {
        Py_DECREF(buf);
        return NULL;
    }
    _PyString_Resize(&buf, buflen);
    return buf;
}

static PyObject *
irsock_connect(PyIrSockObject *s, PyObject *args)
{
    struct sockaddr_irda* addr;
    int daddr = 0;
    char *service = NULL;
    int res;
    int timeout;
    
    addr=&(s->ir);
    if (!PyArg_ParseTuple(args, "is", &daddr, &service)) {
        return NULL;
    }
#ifndef MS_WINDOWS
    addr->sir_family = AF_IRDA;
    strncpy(addr->sir_name, service, 25);
    addr->sir_addr = daddr;
    addr->sir_lsap_sel = LSAP_ANY;
#else
    addr->irdaAddressFamily = AF_IRDA;
    strncpy(addr->irdaServiceName, service, 25);
    memcpy(addr->irdaDeviceID, &daddr, 4);
#endif
    
    Py_BEGIN_ALLOW_THREADS
    res = internal_connect(s, (struct sockaddr *)addr, sizeof(struct sockaddr_irda), &timeout);
    Py_END_ALLOW_THREADS
    
    if (timeout) {
        return NULL;
    }
    if (res != 0) {
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

/* s.close() method.
   Set the file descriptor to -1 so operations tried subsequently
   will surely fail. */

static PyObject *
irsock_close(PyIrSockObject *s)
{
    int fd;

    if ((fd = s->sock_fd) != -1) {
        s->sock_fd = -1;
        Py_BEGIN_ALLOW_THREADS
        (void) SOCKETCLOSE(fd);
        Py_END_ALLOW_THREADS
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
irsock_sendall(PyIrSockObject *s, PyObject *args)
{
    char *buf;
    int len, n = 0, flags = 0, timeout;

    if (!PyArg_ParseTuple(args, "s#|i:sendall", &buf, &len, &flags))
        return NULL;

    if (!IS_SELECTABLE(s)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    do {
        timeout = internal_select(s, 1);
        if (timeout)
            break;
        n = send(s->sock_fd, buf, len, flags);
        if (n < 0)
            break;
        buf += n;
        len -= n;
    } while (len > 0);
    Py_END_ALLOW_THREADS

    if (timeout) {
        return NULL;
    }
    if (n < 0) {
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
irsock_recv(PyIrSockObject *s, PyObject *args)
{
    int len, n = 0, flags = 0, timeout;
    PyObject *buf;

    if (!PyArg_ParseTuple(args, "i|i:recv", &len, &flags))
        return NULL;

    if (len < 0) {
        PyErr_SetString(PyExc_ValueError,
                "negative buffersize in recv");
        return NULL;
    }

    buf = PyString_FromStringAndSize((char *) 0, len);
    if (buf == NULL)
        return NULL;

    if (!IS_SELECTABLE(s)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    timeout = internal_select(s, 0);
    if (!timeout)
        n = recv(s->sock_fd, PyString_AS_STRING(buf), len, flags);
    Py_END_ALLOW_THREADS

    if (timeout) {
        Py_DECREF(buf);
        return NULL;
    }
    if (n < 0) {
        Py_DECREF(buf);
        return NULL;
    }
    if (n != len)
        _PyString_Resize(&buf, n);
    return buf;
}

static PyObject *
irsock_settimeout(PyIrSockObject *s, PyObject *arg)
{
    double timeout;
    
    if (arg == Py_None) {
        timeout = -1.0;
    } else {
        timeout = PyFloat_AsDouble(arg);
        if (timeout < 0.0) {
            if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError, "Timeout value out of range");
        }
    }
    s->sock_timeout = timeout;
    internal_setblocking(s, timeout < 0.0);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
irsock_gettimeout(PyIrSockObject *s)
{
    if (s->sock_timeout < 0.0) {
        Py_INCREF(Py_None);
        return Py_None;
    } else {
        return PyFloat_FromDouble(s->sock_timeout);
    }
}

static PyMethodDef irsock_methods[] = {
    {"getsockopt", (PyCFunction)irsock_getsockopt, METH_VARARGS, irsock_doc},
    {"connect", (PyCFunction)irsock_connect, METH_O, irsock_doc},
    {"close", (PyCFunction)irsock_close, METH_NOARGS, irsock_doc},
    {"sendall", (PyCFunction)irsock_sendall, METH_VARARGS, irsock_doc},
    {"recv", (PyCFunction)irsock_recv, METH_VARARGS, irsock_doc},
    {"settimeout", (PyCFunction)irsock_settimeout, METH_O, irsock_doc},
    {"gettimeout", (PyCFunction)irsock_gettimeout, METH_NOARGS, irsock_doc},
    {NULL}  /* Sentinel */
};

static PyTypeObject irsock_type = {
    PyObject_HEAD_INIT(NULL)
    0,
    "_irsocket.socket",
    sizeof(PyIrSockObject),
    0,
    (destructor)irsock_dealloc,
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    irsock_doc,
    0,                          /* tp_traverse */
    0,                          /* tp_clear */
    0,                          /* tp_richcompare */
    0,                          /* tp_weaklistoffset */
    0,                          /* tp_iter */
    0,                          /* tp_iternext */
    irsock_methods,
    0,                          /* tp_members */
    0,                          /* tp_getset */
    0,                          /* tp_base */
    0,                          /* tp_dict */
    0,                          /* tp_descr_get */
    0,                          /* tp_descr_set */
    0,                          /* tp_dictoffset */
    (initproc)irsock_init,
    0,
    irsock_new,
    
};

/* List of functions exported by this module. */
static PyMethodDef irsocket_methods[] = {
    {NULL}  /* Sentinel */
};

#ifdef MS_WINDOWS
#define OS_INIT_DEFINED
static void
os_cleanup(void)
{
    WSACleanup();
}
static int
os_init(void)
{
    WSADATA WSAData;
    int ret;
    char buf[100];
    ret = WSAStartup(0x0101, &WSAData);
    switch (ret) {
        case 0: /* No error */
            Py_AtExit(os_cleanup);
            return 1; /* Success */
        case WSASYSNOTREADY:
            PyErr_SetString(PyExc_ImportError,
                "WSAStartup failed: network not ready");
            break;
        case WSAVERNOTSUPPORTED:
        case WSAEINVAL:
            PyErr_SetString(PyExc_ImportError,
                "WSAStartup failed: requested version not supported");
            break;
        default:
            PyOS_snprintf(buf, sizeof(buf),
                "WSAStartup failed: error code %d", ret);
            PyErr_SetString(PyExc_ImportError, buf);
            break;
    }
    return 0;
}
#endif

#ifndef OS_INIT_DEFINED
static int
os_init(void)
{
    return 1;
}
#endif

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_irsocket(void)
{
    PyObject *m;
    
    if (!os_init()) {
        return;
    }
    
    if (PyType_Ready(&irsock_type) < 0) {
        return;
    }
    m = Py_InitModule3("_irsocket", irsocket_methods, irsock_doc);
    if (m == NULL) {
        return;
    }
    Py_INCREF(&irsock_type);
    PyModule_AddObject(m, "socket", (PyObject *)&irsock_type);
    PyModule_AddIntConstant(m, "SOL_IRLMP", SOL_IRLMP);
    PyModule_AddIntConstant(m, "IRLMP_ENUMDEVICES", IRLMP_ENUMDEVICES);
}